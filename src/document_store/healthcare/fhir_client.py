"""
FHIR API client for healthcare data access.

Supports HL7 FHIR standard for interoperable healthcare data exchange.
"""

from typing import Dict, Any, Optional, List
import logging
import requests

logger = logging.getLogger(__name__)


class FHIRClient:
    """
    Client for accessing healthcare data via FHIR API.
    
    Supports HL7 FHIR standard for interoperable healthcare data.
    """

    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        api_version: str = "R4",
    ):
        """
        Initialize FHIR client.
        
        Args:
            base_url: FHIR server base URL
            auth_token: Optional authentication token
            api_version: FHIR API version (default: R4)
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.api_version = api_version
        self.headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        
        logger.info(f"FHIRClient initialized: {base_url} (FHIR {api_version})")

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve patient resource via FHIR API.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Patient resource as dictionary
        """
        url = f"{self.base_url}/Patient/{patient_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error retrieving patient {patient_id}: {e}")
            raise

    def search_patients(self, search_params: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Search for patients using FHIR search parameters.
        
        Args:
            search_params: FHIR search parameters (e.g., {'name': 'John'})
            
        Returns:
            List of patient resources
        """
        url = f"{self.base_url}/Patient"
        params = search_params
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            bundle = response.json()
            
            # Extract patient resources from bundle
            patients = []
            if bundle.get("resourceType") == "Bundle":
                for entry in bundle.get("entry", []):
                    if entry.get("resource", {}).get("resourceType") == "Patient":
                        patients.append(entry["resource"])
            
            return patients
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            raise

    def get_encounters(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve patient encounters via FHIR API.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of encounter resources
        """
        url = f"{self.base_url}/Encounter"
        params = {"subject": f"Patient/{patient_id}"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            bundle = response.json()
            
            encounters = []
            if bundle.get("resourceType") == "Bundle":
                for entry in bundle.get("entry", []):
                    if entry.get("resource", {}).get("resourceType") == "Encounter":
                        encounters.append(entry["resource"])
            
            return encounters
        except Exception as e:
            logger.error(f"Error retrieving encounters: {e}")
            raise

    def get_observations(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve patient observations (lab results, vitals) via FHIR API.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of observation resources
        """
        url = f"{self.base_url}/Observation"
        params = {"subject": f"Patient/{patient_id}"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            bundle = response.json()
            
            observations = []
            if bundle.get("resourceType") == "Bundle":
                for entry in bundle.get("entry", []):
                    if entry.get("resource", {}).get("resourceType") == "Observation":
                        observations.append(entry["resource"])
            
            return observations
        except Exception as e:
            logger.error(f"Error retrieving observations: {e}")
            raise

    def get_patient_summary_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive patient data for summarization.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary containing patient, encounters, and observations
        """
        patient = self.get_patient(patient_id)
        encounters = self.get_encounters(patient_id)
        observations = self.get_observations(patient_id)
        
        return {
            "patient": patient,
            "encounters": encounters,
            "observations": observations,
        }

