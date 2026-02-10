"""
AI Decision Engine for the DPS Agent Booking System.
Analyzes user profiles and determines the optimal DPS service type,
booking criteria, and slot scoring strategy.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# ─── Service Type Mappings ───────────────────────────────────────────

DPS_SERVICES = {
    "first_time_dl": {
        "name": "Apply for first time Texas DL/Permit",
        "button_text": ["apply", "first time", "texas dl", "permit"],
        "description": "For people who have never held a Texas driver license"
    },
    "renew_dl": {
        "name": "Renew Texas DL/ID",
        "button_text": ["renew"],
        "description": "For renewing an existing Texas DL or ID card"
    },
    "replace_dl": {
        "name": "Replace Texas DL/ID",
        "button_text": ["replace"],
        "description": "For replacing a lost, stolen, or damaged Texas DL or ID"
    },
    "transfer_oos": {
        "name": "Transfer out-of-state DL to Texas",
        "button_text": ["transfer", "out-of-state", "out of state"],
        "description": "For transferring a valid out-of-state license to Texas"
    },
    "cdl": {
        "name": "Commercial Driver License (CDL)",
        "button_text": ["commercial", "cdl"],
        "description": "For commercial driver license services"
    },
    "texas_id": {
        "name": "Apply for Texas ID card",
        "button_text": ["id card", "texas id"],
        "description": "For applying for a Texas identification card (non-driver)"
    },
    "change_update": {
        "name": "Change/update information on DL/ID",
        "button_text": ["change", "update"],
        "description": "For updating name, address, or other info on your DL/ID"
    },
    "permit": {
        "name": "Apply for Learner Permit",
        "button_text": ["learner", "permit"],
        "description": "For teens under 18 applying for a learner permit"
    },
}


class DecisionEngine:
    """
    Intelligent decision engine that analyzes user profiles and determines:
    1. The correct DPS service type
    2. Optimal booking criteria
    3. Slot priority scoring
    """

    def analyze_profile(self, profile: Dict) -> Dict:
        """
        Analyze a user profile and return a complete recommendation.

        Args:
            profile: User profile dictionary with license situation fields.

        Returns:
            Dictionary with recommended_service, confidence, reasoning, and booking_tips.
        """
        service_key, confidence, reasoning = self._determine_service(profile)
        service_info = DPS_SERVICES[service_key]
        tips = self._generate_booking_tips(profile, service_key)

        return {
            "recommended_service": service_info["name"],
            "service_key": service_key,
            "confidence": confidence,
            "reasoning": reasoning,
            "booking_tips": tips,
            "button_keywords": service_info["button_text"],
            "description": service_info["description"],
        }

    def _determine_service(self, profile: Dict) -> Tuple[str, float, str]:
        """
        Rule-based service type determination.

        Returns:
            Tuple of (service_key, confidence, reasoning)
        """
        has_tx = profile.get("has_texas_license", False)
        has_oos = profile.get("has_out_of_state_license", False)
        expired = profile.get("license_expired", False)
        lost_stolen = profile.get("license_lost_stolen", False)
        commercial = profile.get("is_commercial", False)
        id_only = profile.get("id_only", False)
        needs_permit = profile.get("needs_permit", False)
        age = profile.get("age")

        # ── Priority-ordered rules ──────────────────────────────

        # Rule 1: Commercial license
        if commercial:
            return ("cdl", 0.95, "User needs commercial driving services (CDL).")

        # Rule 2: ID-only (no driving)
        if id_only:
            return ("texas_id", 0.95, "User needs a Texas identification card, not a driver license.")

        # Rule 3: Learner permit (under 18 or explicit)
        if needs_permit or (age is not None and age < 18):
            return ("permit", 0.95,
                    f"User needs a learner permit"
                    f"{f' (age {age}, under 18)' if age and age < 18 else ''}.")

        # Rule 4: Lost/stolen replacement
        if has_tx and lost_stolen:
            return ("replace_dl", 0.95, "User has a Texas DL that was lost or stolen and needs a replacement.")

        # Rule 5: Renewal (has TX license, expired or near expiry)
        if has_tx and expired:
            return ("renew_dl", 0.95, "User has an expired Texas DL and needs to renew.")

        # Rule 6: Transfer out-of-state
        if has_oos and not has_tx:
            return ("transfer_oos", 0.90,
                    "User has an out-of-state license and needs to transfer it to Texas.")

        # Rule 7: Has TX license but needs update
        if has_tx and not expired and not lost_stolen:
            return ("change_update", 0.70,
                    "User has a valid Texas DL. Assuming they need to update information. "
                    "If they need a different service, please update your profile.")

        # Rule 8: Default - first-time Texas DL (no existing license)
        if not has_tx and not has_oos:
            age_note = ""
            if age is not None:
                if age >= 18:
                    age_note = f" User is {age} years old, eligible for full DL."
                else:
                    # Should have been caught by permit rule, but just in case
                    return ("permit", 0.85,
                            f"User is {age}, under 18 — recommending learner permit instead of full DL.")
            return ("first_time_dl", 0.90,
                    f"User has no existing Texas or out-of-state license. "
                    f"Recommending first-time Texas DL application.{age_note}")

        # Fallback
        return ("first_time_dl", 0.50,
                "Could not confidently determine service type from the provided information. "
                "Defaulting to first-time DL application. Please review and update if needed.")

    def _generate_booking_tips(self, profile: Dict, service_key: str) -> List[str]:
        """Generate helpful booking tips based on the user's situation."""
        tips = []

        # General tips
        tips.append("Have all required documents ready before your appointment.")
        tips.append("Arrive 15 minutes early to your appointment.")

        # Service-specific tips
        if service_key == "first_time_dl":
            tips.append("Bring proof of identity (passport or birth certificate).")
            tips.append("Bring proof of Social Security number.")
            tips.append("Bring two proofs of Texas residency (utility bills, lease, etc.).")
            tips.append("You will need to pass a written knowledge test and driving test.")

        elif service_key == "renew_dl":
            tips.append("Bring your expiring/expired Texas DL.")
            tips.append("If expired more than 2 years, you may need to retake tests.")

        elif service_key == "replace_dl":
            tips.append("Bring another form of photo ID if possible.")
            tips.append("You may need to file a police report if your license was stolen.")

        elif service_key == "transfer_oos":
            tips.append("Bring your valid out-of-state license.")
            tips.append("Bring proof of Texas residency.")
            tips.append("Your out-of-state license will be collected by DPS.")

        elif service_key == "cdl":
            tips.append("Bring your current DL and any existing CDL.")
            tips.append("You will need a valid DOT medical card.")
            tips.append("Study the CDL manual for the appropriate vehicle class.")

        elif service_key == "texas_id":
            tips.append("Bring proof of identity (passport or birth certificate).")
            tips.append("Bring proof of Social Security number.")
            tips.append("Bring two proofs of Texas residency.")

        elif service_key == "permit":
            tips.append("A parent or legal guardian must accompany you.")
            tips.append("Bring proof of enrollment in a driver education course.")
            tips.append("Bring parent/guardian consent form (if under 18).")

        # Location tips
        location = profile.get("location_preference", "Denton")
        tips.append(f"Monitoring {location} area locations for the earliest appointments.")

        return tips

    def score_slot(self, slot_date_str: str, priority: str = "any") -> float:
        """
        Score an appointment slot based on how desirable it is.

        Args:
            slot_date_str: Date string in MM/DD/YYYY format.
            priority: One of 'same_day', 'next_day', 'this_week', 'any'.

        Returns:
            Score from 0.0 (worst) to 1.0 (best).
        """
        try:
            slot_date = datetime.strptime(slot_date_str, "%m/%d/%Y").date()
        except ValueError:
            return 0.1  # Invalid date format gets low score

        today = date.today()
        delta = (slot_date - today).days

        if delta < 0:
            return 0.0  # Past date

        # Base scoring: sooner = better
        if delta == 0:
            base_score = 1.0  # Same day = perfect
        elif delta == 1:
            base_score = 0.90  # Next day = great
        elif delta <= 3:
            base_score = 0.75  # Within 3 days
        elif delta <= 7:
            base_score = 0.60  # This week
        elif delta <= 14:
            base_score = 0.40  # Within 2 weeks
        elif delta <= 30:
            base_score = 0.25  # Within a month
        else:
            base_score = 0.10  # More than a month away

        # Priority boost
        if priority == "same_day" and delta == 0:
            base_score = 1.0
        elif priority == "same_day" and delta > 0:
            base_score *= 0.5  # Penalize non-same-day when priority is same_day
        elif priority == "next_day" and delta <= 1:
            base_score = max(base_score, 0.95)
        elif priority == "this_week" and delta <= 7:
            base_score = max(base_score, 0.80)

        return round(base_score, 2)  # type: ignore

    def rank_slots(self, dates: List[str], priority: str = "any") -> List[Dict]:
        """
        Rank a list of appointment dates by desirability.

        Args:
            dates: List of date strings in MM/DD/YYYY format.
            priority: Slot priority preference.

        Returns:
            List of dicts with 'date' and 'score', sorted best-first.
        """
        scored = [
            {"date": d, "score": self.score_slot(d, priority)}
            for d in dates
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def should_auto_book(self, best_slot: Dict, threshold: float = 0.5) -> bool:
        """
        Determine if the agent should auto-book the best available slot.

        Args:
            best_slot: Dict with 'date' and 'score' from rank_slots.
            threshold: Minimum score to trigger auto-booking.

        Returns:
            True if the agent should proceed with booking.
        """
        return best_slot.get("score", 0) >= threshold
