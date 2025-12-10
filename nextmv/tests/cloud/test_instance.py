import unittest

from nextmv.cloud.instance import InstanceConfiguration


class TestInstanceConfigurationValidation(unittest.TestCase):
    """Test validation logic in InstanceConfiguration.model_post_init."""

    def test_no_integration_id_no_validation(self):
        """Test that validation is skipped when integration_id is None or empty."""
        # With None integration_id
        config = InstanceConfiguration(integration_id=None, execution_class="small")
        self.assertEqual(config.execution_class, "small")

        # With empty string integration_id
        config = InstanceConfiguration(integration_id="", execution_class="large")
        self.assertEqual(config.execution_class, "large")

        # With no integration_id specified
        config = InstanceConfiguration(execution_class="medium")
        self.assertEqual(config.execution_class, "medium")

    def test_integration_id_with_integration_execution_class(self):
        """Test that integration_id with execution_class='integration' is valid."""
        config = InstanceConfiguration(integration_id="int-12345", execution_class="integration")
        self.assertEqual(config.integration_id, "int-12345")
        self.assertEqual(config.execution_class, "integration")

    def test_integration_id_with_none_execution_class(self):
        """Test that integration_id with execution_class=None sets it to 'integration'."""
        config = InstanceConfiguration(integration_id="int-12345", execution_class=None)
        self.assertEqual(config.integration_id, "int-12345")
        self.assertEqual(config.execution_class, "integration")

    def test_integration_id_without_execution_class(self):
        """Test that integration_id without execution_class sets it to 'integration'."""
        config = InstanceConfiguration(integration_id="int-12345")
        self.assertEqual(config.integration_id, "int-12345")
        self.assertEqual(config.execution_class, "integration")

    def test_integration_id_with_empty_execution_class(self):
        """Test that integration_id with execution_class='' sets it to 'integration'."""
        config = InstanceConfiguration(integration_id="int-12345", execution_class="")
        self.assertEqual(config.integration_id, "int-12345")
        self.assertEqual(config.execution_class, "integration")

    def test_integration_id_with_invalid_execution_class_raises_error(self):
        """Test that integration_id with non-integration execution_class raises ValueError."""
        invalid_classes = ["small", "medium", "large", "custom", "standard"]

        for execution_class in invalid_classes:
            with self.subTest(execution_class=execution_class):
                with self.assertRaises(ValueError) as context:
                    InstanceConfiguration(integration_id="int-12345", execution_class=execution_class)

                error_msg = str(context.exception)
                self.assertIn("When integration_id is set", error_msg)
                self.assertIn("execution_class must be `integration` or None", error_msg)

    def test_integration_id_error_message_format(self):
        """Test that the error message contains the expected format."""
        with self.assertRaises(ValueError) as context:
            InstanceConfiguration(integration_id="int-12345", execution_class="custom")

        error_msg = str(context.exception)
        # When using model_post_init, Pydantic wraps the error message
        self.assertIn("When integration_id is set, execution_class must be `integration` or None.", error_msg)

    def test_integration_id_with_other_configuration_options(self):
        """Test that integration_id works correctly with other configuration options."""
        config = InstanceConfiguration(
            integration_id="int-12345", options={"max_runtime": 30}, secrets_collection_id="sc_1234567890"
        )
        self.assertEqual(config.integration_id, "int-12345")
        self.assertEqual(config.execution_class, "integration")
        self.assertEqual(config.options, {"max_runtime": 30})
        self.assertEqual(config.secrets_collection_id, "sc_1234567890")

    def test_no_integration_id_with_other_options(self):
        """Test configuration without integration_id but with other options."""
        config = InstanceConfiguration(
            execution_class="small", options={"max_runtime": 60}, secrets_collection_id="sc_9876543210"
        )
        self.assertEqual(config.execution_class, "small")
        self.assertEqual(config.options, {"max_runtime": 60})
        self.assertEqual(config.secrets_collection_id, "sc_9876543210")
        self.assertIsNone(config.integration_id)
