"""Handles username/password authentication and two-step authentication"""

import sys
import click
import pyicloud
from icloudpd.logger import setup_logger


class TwoStepAuthRequiredError(Exception):
    """
    Raised when 2SA is required. base.py catches this exception
    and sends an email notification.
    """

def authenticator(domain):
    """Wraping authentication with domain context"""
    def authenticate_(
            username,
            password,
            cookie_directory=None,
            raise_error_on_2sa=False,
            client_id=None,
    ):
        """Authenticate with iCloud username and password"""
        logger = setup_logger()
        logger.debug("Authenticating...")
        while True:
            try:
                # If password not provided on command line variable will be set to None
                # and PyiCloud will attempt to retrieve from its keyring
                icloud = pyicloud.PyiCloudService(
                    domain,
                    username, password,
                    cookie_directory=cookie_directory,
                    client_id=client_id,
                    )
                break
            except pyicloud.exceptions.PyiCloudNoStoredPasswordAvailableException:
                # Prompt for password if not stored in PyiCloud's keyring
                password = click.prompt("iCloud Password", hide_input=True)

        if icloud.requires_2sa:
            if raise_error_on_2sa:
                raise TwoStepAuthRequiredError(
                    "Two-step/two-factor authentication is required!"
                )
        two_factor_authenticate(icloud, logger)
        return icloud
    return authenticate_


def request_2sa(icloud, logger):
    """Request two-step authentication. Prompts for SMS or device"""
    devices = icloud.trusted_devices
    devices_count = len(devices)
    device_index = 0
    if devices_count > 0:
        for i, device in enumerate(devices):
            # pylint: disable-msg=consider-using-f-string
            print(
                "  %s: %s" %
                (i, device.get(
                    "deviceName", "SMS to %s" %
                    device.get("phoneNumber"))))
            # pylint: enable-msg=consider-using-f-string

        # pylint: disable-msg=superfluous-parens
        print(f"  {devices_count}: Enter two-factor authentication code")
        # pylint: enable-msg=superfluous-parens
        device_index = click.prompt(
            "Please choose an option:",
            default=0,
            type=click.IntRange(
                0,
                devices_count))

    if device_index == devices_count:
        # We're using the 2FA code that was automatically sent to the user's device,
        # so can just use an empty dict()
        device = {}
    else:
        device = devices[device_index]
        if not icloud.send_verification_code(device):
            logger.error("Failed to send two-factor authentication code")
            sys.exit(1)

    code = click.prompt("Please enter two-factor authentication code")
    if not icloud.validate_verification_code(device, code):
        logger.error("Failed to verify two-factor authentication code")
        sys.exit(1)
    logger.info(
        "Great, you're all set up. The script can now be run without "
        "user interaction until 2SA expires.\n"
        "You can set up email notifications for when "
        "the two-step authentication expires.\n"
        "(Use --help to view information about SMTP options.)"
    )

def two_factor_authenticate(icloud, logging):
    if icloud.requires_2fa:
        logging.info("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = icloud.validate_2fa_code(code)
        logging.info("Code validation result: %s" % result)

        if not result:
            logging.error("Failed to verify security code")
            sys.exit(1)

        if not icloud.is_trusted_session:
            logging.warning("Session is not trusted. Requesting trust...")
            result = icloud.trust_session()
            logging.info("Session trust result %s" % result)

            if not result:
                logging.error(
                    "Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    elif icloud.requires_2sa:
        logging.info("Two-step authentication required. Your trusted devices are:")

        devices = icloud.trusted_devices
        for i, device in enumerate(devices):
            logging.info(
                "  %s: %s" % (i, device.get('deviceName',
                                            "SMS to %s" % device.get('phoneNumber')))
            )

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not icloud.send_verification_code(device):
            logging.error("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not icloud.validate_verification_code(device, code):
            logging.info("Failed to verify verification code")
            sys.exit(1)