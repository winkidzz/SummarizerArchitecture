"""
BigQuery connector for healthcare data access.

Provides direct access to BigQuery for patient data, encounters,
and other healthcare information for RAG summarization.
"""

from typing import Dict, Any, Optional, List
import logging

try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    bigquery = None

logger = logging.getLogger(__name__)


class BigQueryConnector:
    """
    Connector for accessing healthcare data from BigQuery.
    
    Supports direct queries, streaming data, and real-time access.
    """

    def __init__(
        self,
        project_id: str,
        dataset_id: Optional[str] = None,
        location: str = "US",
    ):
        """
        Initialize BigQuery connector.
        
        Args:
            project_id: Google Cloud project ID
            dataset_id: Optional default dataset ID
            location: BigQuery location
        """
        if not BIGQUERY_AVAILABLE:
            raise ImportError(
                "google-cloud-bigquery is not installed. "
                "Install it with: pip install google-cloud-bigquery"
            )
        
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.location = location
        self.client = bigquery.Client(project=project_id, location=location)
        
        logger.info(f"BigQueryConnector initialized: project={project_id}, dataset={dataset_id}")

    def query_patients(
        self,
        patient_id: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query patient data from BigQuery.
        
        Args:
            patient_id: Optional specific patient ID
            query_params: Optional additional query parameters
            
        Returns:
            List of patient records
        """
        if patient_id:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.patients`
            WHERE patient_id = @patient_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("patient_id", "STRING", patient_id)
                ]
            )
        else:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.patients`
            LIMIT 100
            """
            job_config = None
        
        try:
            results = self.client.query(query, job_config=job_config)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error querying patients: {e}")
            raise

    def query_encounters(
        self,
        patient_id: str,
        date_range: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query patient encounters from BigQuery.
        
        Args:
            patient_id: Patient ID
            date_range: Optional date range {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
            
        Returns:
            List of encounter records
        """
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.encounters`
        WHERE patient_id = @patient_id
        """
        
        params = [bigquery.ScalarQueryParameter("patient_id", "STRING", patient_id)]
        
        if date_range:
            query += " AND encounter_date BETWEEN @start_date AND @end_date"
            params.extend([
                bigquery.ScalarQueryParameter("start_date", "DATE", date_range['start']),
                bigquery.ScalarQueryParameter("end_date", "DATE", date_range['end']),
            ])
        
        query += " ORDER BY encounter_date DESC"
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        
        try:
            results = self.client.query(query, job_config=job_config)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error querying encounters: {e}")
            raise

    def stream_insert(self, table_id: str, rows: List[Dict[str, Any]]) -> None:
        """
        Stream insert data into BigQuery table.
        
        Args:
            table_id: Table ID
            rows: List of row dictionaries
        """
        table_ref = self.client.dataset(self.dataset_id).table(table_id)
        table = self.client.get_table(table_ref)
        
        errors = self.client.insert_rows_json(table, rows)
        if errors:
            logger.error(f"BigQuery insert errors: {errors}")
            raise ValueError(f"BigQuery insert failed: {errors}")
        
        logger.info(f"Inserted {len(rows)} rows into {table_id}")

    def get_patient_summary_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient data for summarization.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with patient, encounters, and related data
        """
        patients = self.query_patients(patient_id=patient_id)
        encounters = self.query_encounters(patient_id=patient_id)
        
        return {
            "patient": patients[0] if patients else None,
            "encounters": encounters,
        }

