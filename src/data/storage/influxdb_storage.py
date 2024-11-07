from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from .base_storage import BaseTimeSeriesStorage

class InfluxDBStorage(BaseTimeSeriesStorage):
    """InfluxDB implementation of time series storage."""
    
    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        verify_ssl: bool = True
    ):
        """
        Initialize InfluxDB client.
        
        Args:
            url: InfluxDB server URL
            token: Authentication token
            org: Organization name
            bucket: Default bucket name
            verify_ssl: Whether to verify SSL certificates
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.verify_ssl = verify_ssl
        self.client = None
        self.write_api = None
        self.query_api = None
        
    async def connect(self) -> bool:
        """Establish connection to InfluxDB."""
        try:
            self.client = influxdb_client.InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
                verify_ssl=self.verify_ssl
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            
            # Test connection
            health = self.client.health()
            return health.status == 'pass'
            
        except Exception as e:
            print(f"Error connecting to InfluxDB: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Close InfluxDB connection."""
        if self.client:
            self.client.close()
    
    async def write_data(
        self,
        measurement: str,
        data: pd.DataFrame,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Write time series data to InfluxDB."""
        try:
            if tags is None:
                tags = {}
                
            # Convert DataFrame to InfluxDB line protocol
            records = []
            for index, row in data.iterrows():
                fields = {col: row[col] for col in data.columns}
                point = influxdb_client.Point(measurement)\
                    .time(index)\
                    .fields(fields)
                    
                # Add tags
                for tag_key, tag_value in tags.items():
                    point = point.tag(tag_key, tag_value)
                    
                records.append(point)
                
            # Write data
            self.write_api.write(bucket=self.bucket, record=records)
            return True
            
        except Exception as e:
            print(f"Error writing to InfluxDB: {str(e)}")
            return False
    
    async def read_data(
        self,
        measurement: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Read time series data from InfluxDB."""
        try:
            # Construct Flux query
            query = f'from(bucket: "{self.bucket}")'
            query += f' |> range(start: {start_time.isoformat() if start_time else "-30d"}'
            query += f', stop: {end_time.isoformat() if end_time else "now()"})'
            query += f' |> filter(fn: (r) => r["_measurement"] == "{measurement}")'
            
            # Add tag filters
            if tags:
                for tag_key, tag_value in tags.items():
                    query += f' |> filter(fn: (r) => r["{tag_key}"] == "{tag_value}")'
            
            # Add field filters
            if fields:
                field_list = '", "'.join(fields)
                query += f' |> filter(fn: (r) => contains(value: r["_field"], set: ["{field_list}"]))'
            
            # Execute query
            result = self.query_api.query_data_frame(query=query, org=self.org)
            
            if isinstance(result, list):
                if not result:
                    return pd.DataFrame()
                result = pd.concat(result)
                
            # Clean up and pivot the result
            if not result.empty:
                result = result.pivot(
                    index='_time',
                    columns='_field',
                    values='_value'
                )
                
            return result
            
        except Exception as e:
            print(f"Error reading from InfluxDB: {str(e)}")
            return pd.DataFrame()
    
    async def delete_data(
        self,
        measurement: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Delete time series data from InfluxDB."""
        try:
            # Construct delete predicate
            predicate = f'_measurement="{measurement}"'
            if tags:
                for tag_key, tag_value in tags.items():
                    predicate += f' AND {tag_key}="{tag_value}"'
                    
            # Execute delete
            delete_api = self.client.delete_api()
            delete_api.delete(
                start=start_time,
                stop=end_time,
                predicate=predicate,
                bucket=self.bucket,
                org=self.org
            )
            return True
            
        except Exception as e:
            print(f"Error deleting from InfluxDB: {str(e)}")
            return False
    
    async def list_measurements(self) -> List[str]:
        """List all available measurements in InfluxDB."""
        try:
            query = f'''
                import "influxdata/influxdb/schema"
                schema.measurements(bucket: "{self.bucket}")
            '''
            result = self.query_api.query(query=query, org=self.org)
            
            measurements = []
            for table in result:
                for record in table.records:
                    measurements.append(record.values.get('_value'))
                    
            return measurements
            
        except Exception as e:
            print(f"Error listing measurements: {str(e)}")
            return []
    
    async def get_latest_timestamp(
        self,
        measurement: str,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[datetime]:
        """Get latest timestamp for a measurement in InfluxDB."""
        try:
            query = f'from(bucket: "{self.bucket}")'
            query += f' |> range(start: -30d)'
            query += f' |> filter(fn: (r) => r["_measurement"] == "{measurement}")'
            
            # Add tag filters
            if tags:
                for tag_key, tag_value in tags.items():
                    query += f' |> filter(fn: (r) => r["{tag_key}"] == "{tag_value}")'
                    
            query += ' |> last()'
            
            result = self.query_api.query_data_frame(query=query, org=self.org)
            
            if isinstance(result, list):
                if not result:
                    return None
                result = pd.concat(result)
                
            if not result.empty:
                return pd.to_datetime(result['_time'].iloc[0])
                
            return None
            
        except Exception as e:
            print(f"Error getting latest timestamp: {str(e)}")
            return None
