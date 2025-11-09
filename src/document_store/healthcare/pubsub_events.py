"""
Pub/Sub event handler for real-time healthcare data events.

Processes real-time events from BigQuery/Spanner via Pub/Sub
for event-driven healthcare summarization.
"""

from typing import Dict, Any, Callable, Optional
import logging
import json

try:
    from google.cloud import pubsub_v1
    PUBSUB_AVAILABLE = True
except ImportError:
    PUBSUB_AVAILABLE = False
    pubsub_v1 = None

logger = logging.getLogger(__name__)


class PubSubEventHandler:
    """
    Handler for real-time Pub/Sub events from healthcare data sources.
    
    Processes events from BigQuery/Spanner for real-time summarization.
    """

    def __init__(
        self,
        project_id: str,
        subscription_id: str,
        event_handler: Optional[Callable] = None,
    ):
        """
        Initialize Pub/Sub event handler.
        
        Args:
            project_id: Google Cloud project ID
            subscription_id: Pub/Sub subscription ID
            event_handler: Optional custom event handler function
        """
        if not PUBSUB_AVAILABLE:
            raise ImportError(
                "google-cloud-pubsub is not installed. "
                "Install it with: pip install google-cloud-pubsub"
            )
        
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.event_handler = event_handler
        
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )
        
        logger.info(
            f"PubSubEventHandler initialized: "
            f"project={project_id}, subscription={subscription_id}"
        )

    def process_event(self, message_data: bytes) -> Dict[str, Any]:
        """
        Process a Pub/Sub event message.
        
        Args:
            message_data: Message data bytes
            
        Returns:
            Processed event data
        """
        try:
            event = json.loads(message_data.decode('utf-8'))
            
            if self.event_handler:
                return self.event_handler(event)
            
            return event
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            raise

    def subscribe(
        self,
        callback: Callable,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Subscribe to Pub/Sub events and process them.
        
        Args:
            callback: Callback function to process events
            timeout: Optional timeout in seconds
        """
        def message_callback(message):
            try:
                event_data = self.process_event(message.data)
                result = callback(event_data)
                message.ack()
                return result
            except Exception as e:
                logger.error(f"Error in message callback: {e}")
                message.nack()
        
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=message_callback,
        )
        
        logger.info(f"Subscribed to {self.subscription_path}")
        
        try:
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            streaming_pull_future.cancel()
            logger.error(f"Subscription error: {e}")
            raise

    def publish_event(
        self,
        topic_id: str,
        event_data: Dict[str, Any],
    ) -> str:
        """
        Publish event to Pub/Sub topic.
        
        Args:
            topic_id: Pub/Sub topic ID
            event_data: Event data dictionary
            
        Returns:
            Message ID
        """
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        
        message_data = json.dumps(event_data).encode('utf-8')
        future = self.publisher.publish(topic_path, message_data)
        
        message_id = future.result()
        logger.info(f"Published event to {topic_path}: {message_id}")
        
        return message_id

