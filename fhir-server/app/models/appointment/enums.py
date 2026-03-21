from enum import Enum


class AppointmentStatus(str, Enum):
    """
    FHIR AppointmentStatus value set.

    The overall status of the appointment.
    """

    proposed = "proposed"  # None of the participant(s) have finalized their acceptance of the appointment request
    pending = "pending"  # Some or all of the participant(s) have not finalized their acceptance of the appointment request
    booked = "booked"  # All participant(s) have finalized their acceptance of the appointment request
    arrived = "arrived"  # The patient has arrived for the appointment
    fulfilled = "fulfilled"  # The appointment has occurred and is complete
    cancelled = "cancelled"  # The appointment has been cancelled before it occurred
    noshow = "noshow"  # The patient did not show up for the appointment
    entered_in_error = (
        "entered-in-error"  # The appointment was entered in error and voided
    )
    checked_in = "checked-in"  # The patient has checked in for the appointment
    waitlist = (
        "waitlist"  # The appointment is on a waitlist, pending an opening to occur
    )
