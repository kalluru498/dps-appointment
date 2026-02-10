import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agent.decision_engine import DecisionEngine

@pytest.fixture
def engine():
    return DecisionEngine()

def test_determine_service_first_time(engine):
    profile = {"has_texas_license": False, "age": 25}
    analysis = engine.analyze_profile(profile)
    assert analysis["service_key"] == "first_time_dl"
    assert analysis["recommended_service"] == "Apply for first time Texas DL/Permit"

def test_determine_service_renew(engine):
    profile = {"has_texas_license": True, "license_expired": True}
    analysis = engine.analyze_profile(profile)
    assert analysis["service_key"] == "renew_dl"

def test_determine_service_replace(engine):
    profile = {"has_texas_license": True, "license_lost_stolen": True}
    analysis = engine.analyze_profile(profile)
    assert analysis["service_key"] == "replace_dl"

def test_determine_service_transfer(engine):
    profile = {"has_out_of_state_license": True, "has_texas_license": False}
    analysis = engine.analyze_profile(profile)
    assert analysis["service_key"] == "transfer_oos"

def test_determine_service_permit_under_18(engine):
    profile = {"age": 16, "has_texas_license": False}
    analysis = engine.analyze_profile(profile)
    assert analysis["service_key"] == "permit"

def test_score_slot(engine):
    from datetime import date, timedelta
    today = date.today()
    s_today = today.strftime("%m/%d/%Y")
    s_tmrw = (today + timedelta(days=1)).strftime("%m/%d/%Y")
    s_week = (today + timedelta(days=5)).strftime("%m/%d/%Y")

    assert engine.score_slot(s_today) == 1.0
    assert engine.score_slot(s_tmrw) >= 0.90
    assert engine.score_slot(s_week) >= 0.60

def test_score_slot_priority(engine):
    from datetime import date, timedelta
    today = date.today()
    s_tmrw = (today + timedelta(days=1)).strftime("%m/%d/%Y")
    
    # Priority same_day penalizes next_day
    score = engine.score_slot(s_tmrw, priority="same_day")
    assert score < 0.90
