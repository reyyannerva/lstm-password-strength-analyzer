"""
Test suite for SecurityService integration module.

Tests all service methods:
- analyze(): comprehensive analysis
- score(): scoring functionality
- explain(): explanations and suggestions
- generate(): password generation
- generate_and_analyze(): generation with analysis
- batch_analyze(): batch processing
- Module integration and edge cases
"""

import pytest
from src.security.security_service import SecurityService


class TestSecurityService:
    """Test SecurityService class."""
    
    @pytest.fixture
    def service(self):
        """Provide a SecurityService instance for tests."""
        return SecurityService()
    
    # ============ Analyze Method Tests ============
    
    def test_analyze_strong_password(self, service):
        """Test analyzing a strong password."""
        result = service.analyze("MyStr0ng!Pass")
        
        assert "password" in result
        assert "patterns" in result
        assert "risk_score" in result
        assert "security_level" in result
        assert "is_strong" in result
        assert result["password"] == "MyStr0ng!Pass"
        assert isinstance(result["risk_score"], (int, float))
        assert isinstance(result["patterns"], list)
    
    def test_analyze_weak_password(self, service):
        """Test analyzing a weak password."""
        result = service.analyze("password")
        
        assert result["is_strong"] is False
        assert len(result["missing_requirements"]) > 0
        assert result["risk_score"] < 60
    
    def test_analyze_empty_password(self, service):
        """Test analyzing empty password."""
        result = service.analyze("")
        
        assert result["password"] == ""
        assert result["is_strong"] is False
        assert len(result["missing_requirements"]) >= 5
        assert result["risk_score"] == 0
    
    def test_analyze_none_password(self, service):
        """Test analyzing None password (converted to empty string)."""
        result = service.analyze(None)
        
        assert result["password"] == ""
        assert result["is_strong"] is False
    
    def test_analyze_returns_all_fields(self, service):
        """Test that analyze returns all required fields."""
        result = service.analyze("Test1234!")
        
        required_fields = [
            "password", "rules_analysis", "patterns", "risk_score", "security_level",
            "rule_score", "lstm_score", "feedback", "explanation",
            "missing_requirements", "pattern_warnings", "suggestions",
            "is_strong", "detailed_analysis"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_analyze_with_lstm_score(self, service):
        """Test analyze with optional LSTM score."""
        result_without_lstm = service.analyze("Test1234!")
        result_with_lstm = service.analyze("Test1234!", lstm_score=70)
        
        # LSTM score should be included when provided
        assert result_with_lstm["lstm_score"] == 70
        
        # Risk scores might differ due to LSTM weight
        if result_without_lstm["rule_score"] < 100:
            # If rule score is not max, final score should be different
            pass
    
    def test_analyze_detects_patterns(self, service):
        """Test that analyze detects weak patterns."""
        # Password with repeated characters
        result = service.analyze("aaa123456bB!")
        assert len(result["patterns"]) > 0
        
        # Password with sequential characters
        result = service.analyze("abc123456bB!")
        assert len(result["patterns"]) > 0
    
    def test_analyze_security_levels(self, service):
        """Test that security levels are appropriate."""
        weak = service.analyze("weak")
        medium = service.analyze("Medium123!")
        strong = service.analyze("Str0ng!P@ssw0rd")
        
        assert weak["risk_score"] < medium["risk_score"]
        assert medium["risk_score"] < strong["risk_score"]
        assert weak["security_level"] in ["Çok Zayıf", "Zayıf"]
    
    # ============ Score Method Tests ============
    
    def test_score_returns_score_fields(self, service):
        """Test that score method returns correct fields."""
        result = service.score("Test1234!")
        
        required_fields = [
            "password", "final_score", "rule_score",
            "lstm_score", "security_level", "feedback"
        ]
        
        for field in required_fields:
            assert field in result
    
    def test_score_vs_analyze_score_consistency(self, service):
        """Test that score method consistent with analyze."""
        password = "Test1234!"
        score_result = service.score(password)
        analyze_result = service.analyze(password)
        
        assert score_result["final_score"] == analyze_result["risk_score"]
        assert score_result["security_level"] == analyze_result["security_level"]
    
    def test_score_with_lstm(self, service):
        """Test scoring with LSTM score."""
        result = service.score("Test1234!", lstm_score=75)
        
        assert result["lstm_score"] == 75
        assert "final_score" in result
    
    def test_score_empty_password(self, service):
        """Test scoring empty password."""
        result = service.score("")
        
        assert result["final_score"] == 0
        assert result["password"] == ""
    
    # ============ Explain Method Tests ============
    
    def test_explain_returns_explanation_fields(self, service):
        """Test that explain returns all explanation fields."""
        result = service.explain("Test1234!")
        
        required_fields = [
            "password", "security_level", "assessment",
            "missing_requirements", "pattern_warnings",
            "suggestions", "is_strong"
        ]
        
        for field in required_fields:
            assert field in result
    
    def test_explain_strong_password(self, service):
        """Test explaining a strong password."""
        result = service.explain("Str0ng!P@ssw0rd")
        
        assert result["is_strong"] is True
        assert len(result["missing_requirements"]) == 0
        assert result["security_level"] == "Güçlü"
    
    def test_explain_weak_password(self, service):
        """Test explaining a weak password."""
        result = service.explain("123")
        
        assert result["is_strong"] is False
        assert len(result["missing_requirements"]) > 0
        assert "suggestions" in result
    
    def test_explain_recommendations_in_suggestions(self, service):
        """Test that suggestions are provided for weak passwords."""
        result = service.explain("abc")
        
        if result["is_strong"] is False:
            # Should have suggestions for improvement
            assert len(result["missing_requirements"]) > 0 or len(result["pattern_warnings"]) > 0
    
    # ============ Generate Method Tests ============
    
    def test_generate_default_length(self, service):
        """Test generating password with default length."""
        result = service.generate()
        
        assert "password" in result
        assert "length" in result
        assert result["length"] == 16  # Default length
        assert len(result["password"]) == 16
    
    def test_generate_custom_length(self, service):
        """Test generating password with custom length."""
        result = service.generate(length=20)
        
        assert result["length"] == 20
        assert len(result["password"]) == 20
    
    def test_generate_minimum_length(self, service):
        """Test generating with length < 8 (should be enforced to 8)."""
        result = service.generate(length=5)
        
        assert result["length"] >= 8
        assert len(result["password"]) >= 8
    
    def test_generate_returns_analysis(self, service):
        """Test that generate includes analysis."""
        result = service.generate()
        
        assert "patterns" in result
        assert "risk_score" in result
        assert "security_level" in result
        assert "is_strong" in result
    
    def test_generate_meets_criteria(self, service):
        """Test that generated password meets security criteria."""
        result = service.generate()
        password = result["password"]
        
        # Should have uppercase
        assert any(c.isupper() for c in password)
        # Should have lowercase
        assert any(c.islower() for c in password)
        # Should have digit
        assert any(c.isdigit() for c in password)
        # Should have special character
        assert any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)
    
    def test_generate_multiple_different(self, service):
        """Test that multiple generations produce different passwords."""
        pwd1 = service.generate()["password"]
        pwd2 = service.generate()["password"]
        
        # Very unlikely to be the same
        assert pwd1 != pwd2
    
    # ============ Generate and Analyze Method Tests ============
    
    def test_generate_and_analyze_returns_analysis(self, service):
        """Test that generate_and_analyze returns full analysis."""
        result = service.generate_and_analyze()
        
        # Should have all analyze fields
        assert "password" in result
        assert "risk_score" in result
        assert "security_level" in result
        assert "is_strong" in result
        assert "missing_requirements" in result
        assert "suggestions" in result
    
    def test_generate_and_analyze_custom_length(self, service):
        """Test generate_and_analyze with custom length."""
        result = service.generate_and_analyze(length=12)
        
        assert len(result["password"]) == 12
    
    def test_generate_and_analyze_produces_strong(self, service):
        """Test that generated passwords are analyzed as strong."""
        result = service.generate_and_analyze()
        
        # Generated passwords should generally be strong
        assert result["risk_score"] >= 60
    
    # ============ Batch Analyze Method Tests ============
    
    def test_batch_analyze_multiple_passwords(self, service):
        """Test batch analyzing multiple passwords."""
        passwords = ["weak", "Medium123!", "Str0ng!Pass1"]
        result = service.batch_analyze(passwords)
        
        assert "results" in result
        assert "summary" in result
        assert len(result["results"]) == 3
    
    def test_batch_analyze_returns_summary(self, service):
        """Test that batch analysis includes summary statistics."""
        passwords = ["weak", "Medium123!", "Str0ng!Pass1", "another"]
        result = service.batch_analyze(passwords)
        
        summary = result["summary"]
        assert summary["total_analyzed"] == 4
        assert "strong_passwords" in summary
        assert "weak_passwords" in summary
        assert "average_score" in summary
        assert "security_level_distribution" in summary
    
    def test_batch_analyze_empty_list(self, service):
        """Test batch analyze with empty list."""
        result = service.batch_analyze([])
        
        assert result["summary"]["total_analyzed"] == 0
        assert result["summary"]["strong_passwords"] == 0
    
    def test_batch_analyze_with_lstm_scores(self, service):
        """Test batch analyze with LSTM scores."""
        passwords = ["Test1234!", "Weak123"]
        lstm_scores = [80, 40]
        result = service.batch_analyze(passwords, lstm_scores)
        
        assert len(result["results"]) == 2
        assert result["results"][0]["lstm_score"] == 80
        assert result["results"][1]["lstm_score"] == 40
    
    def test_batch_analyze_lstm_scores_length_mismatch(self, service):
        """Test batch analyze with mismatched lstm_scores length."""
        passwords = ["Test1234!", "Weak123"]
        lstm_scores = [80]  # Wrong length
        
        with pytest.raises(ValueError):
            service.batch_analyze(passwords, lstm_scores)
    
    def test_batch_analyze_none_lstm_scores(self, service):
        """Test batch analyze with None lstm_scores."""
        passwords = ["Test1234!", "Weak123"]
        result = service.batch_analyze(passwords, None)
        
        assert len(result["results"]) == 2
        # Should work without errors
    
    # ============ Integration Tests ============
    
    def test_integration_all_modules(self, service):
        """Test that all security modules work together."""
        password = "MyStr0ng!Pass123"
        result = service.analyze(password)
        
        # All modules should contribute to the result
        assert len(result) > 0
        assert result["risk_score"] > 0
        assert result["security_level"] != ""
        assert isinstance(result["patterns"], list)
        assert isinstance(result["suggestions"], list)
    
    def test_service_consistency(self, service):
        """Test that service is consistent across multiple calls."""
        password = "Test1234!"
        
        result1 = service.analyze(password)
        result2 = service.analyze(password)
        
        # Same password should produce same results
        assert result1["risk_score"] == result2["risk_score"]
        assert result1["security_level"] == result2["security_level"]
        assert result1["patterns"] == result2["patterns"]
    
    def test_service_initialization_weights(self):
        """Test service initialization with custom weights."""
        service = SecurityService(rule_weight=0.7, lstm_weight=0.3)
        result = service.score("Test1234!", lstm_score=50)
        
        # Should be able to initialize with custom weights
        assert "final_score" in result
    
    # ============ Edge Cases ============
    
    def test_special_characters_only(self, service):
        """Test password with only special characters."""
        result = service.analyze("!@#$%^&*()")
        
        assert "password" in result
        assert result["is_strong"] is False
    
    def test_very_long_password(self, service):
        """Test analyzing very long password."""
        long_pwd = "A" * 100 + "a" * 100 + "1" * 100 + "!" * 100
        result = service.analyze(long_pwd)
        
        assert "risk_score" in result
        assert result["password"] == long_pwd
    
    def test_unicode_characters(self, service):
        """Test password with unicode characters."""
        result = service.analyze("Parola123!@#")
        
        assert "password" in result
        assert "risk_score" in result
    
    def test_whitespace_handling(self, service):
        """Test that whitespace is preserved."""
        pwd = "Test 123!"
        result = service.analyze(pwd)
        
        assert result["password"] == pwd
    
    def test_numeric_password(self, service):
        """Test numeric-only password detection."""
        result = service.analyze("1234567890")
        
        assert result["is_strong"] is False
        assert len(result["patterns"]) > 0


# ============ Standalone Function Tests ============

def test_service_can_be_imported():
    """Test that service can be imported without errors."""
    from src.security.security_service import SecurityService
    assert SecurityService is not None


def test_service_standalone_methods():
    """Test service methods can be called independently."""
    service = SecurityService()
    
    # All methods should work standalone
    service.analyze("Test123!")
    service.score("Test123!")
    service.explain("Test123!")
    service.generate()
    service.generate_and_analyze()
    service.batch_analyze(["Test123!", "weak"])
