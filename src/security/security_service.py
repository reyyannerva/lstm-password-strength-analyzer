"""
Comprehensive security service that integrates all password security modules.

This service provides:
- Pattern detection (weak pattern identification)
- Risk scoring (rule-based + optional LSTM)
- Password explanation and improvement suggestions
- Secure password generation
- Comprehensive password analysis

The service acts as a unified interface for all security operations.
"""

from typing import Any, Dict, Optional
from src.security.patterns import detect_patterns
from src.security.generator import generate_password
from src.security.risk_scorer import HybridRiskScorer
from src.security.explain import explain_password
from src.security.rules import analyze_rules


class SecurityService:
    """
    Unified security service integrating all password security modules.
    
    Provides methods for:
    - Analyzing passwords (patterns, risk score, explanations)
    - Generating secure passwords
    - Scoring password strength
    - Getting user-friendly explanations
    
    Args:
        lstm_model: Optional LSTM model for predictability scoring.
        rule_weight: Weight for rule-based scoring (default 0.6).
        lstm_weight: Weight for LSTM-based scoring (default 0.4).
    """
    
    def __init__(
        self,
        lstm_model: Optional[Any] = None,
        rule_weight: float = 0.6,
        lstm_weight: float = 0.4,
    ) -> None:
        self.lstm_model = lstm_model
        self.risk_scorer = HybridRiskScorer(rule_weight, lstm_weight)
    
    def analyze(
        self,
        password: str,
        lstm_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive password analysis combining all modules.
        
        Single function call performs:
        1. Rule-based analysis
        2. Pattern detection
        3. Risk scoring (rule-based + optional LSTM)
        4. Explanation and suggestions
        5. Security level determination
        
        Args:
            password: Password text to analyze.
            lstm_score: Optional LSTM score (0-100, higher = safer).
        
        Returns:
            Comprehensive analysis dictionary with:
            - password: The input password
            - rules_analysis: Rule-based check results
            - patterns: List of detected weak patterns
            - risk_score: Numeric security score (0-100)
            - security_level: Human-readable security level (Çok Zayıf - Çok Güçlü)
            - explanation: User-friendly explanation
            - missing_requirements: List of missing security rules
            - suggestions: Actionable improvement suggestions
            - detailed_analysis: Complete scoring details
            - is_strong: Boolean indicating if password meets all criteria
        """
        password = str(password) if password is not None else ""
        
        # 1. Rule-based analysis
        rules_result = analyze_rules(password)
        
        # 2. Detect patterns
        patterns = detect_patterns(password)
        
        # 3. Risk scoring
        risk_result = self.risk_scorer.score(password, lstm_score)
        
        # 4. Explanation and suggestions
        explanation = explain_password(password)
        
        # 5. Combine results
        return {
            "password": password,
            "rules_analysis": {
                "passed_count": rules_result["passed_count"],
                "total_checks": rules_result["total_checks"],
                "all_passed": rules_result["all_passed"],
                "details": rules_result["details"],
            },
            "patterns": patterns,
            "risk_score": risk_result.final_score,
            "security_level": risk_result.security_level,
            "rule_score": risk_result.rule_score,
            "lstm_score": risk_result.lstm_score,
            "feedback": risk_result.feedback,
            "explanation": explanation.get("assessment", ""),
            "missing_requirements": explanation.get("missing_requirements", []),
            "pattern_warnings": explanation.get("pattern_warnings", []),
            "suggestions": explanation.get("suggestions", []),
            "is_strong": explanation.get("is_strong", False) and rules_result["all_passed"],
            "detailed_analysis": {
                "patterns_found": len(patterns),
                "rules_passed": rules_result["passed_count"],
                "rules_total": rules_result["total_checks"],
                "requirements_met": 5 - len(explanation.get("missing_requirements", [])),
                "requirements_total": 5,
                "warnings_count": len(explanation.get("pattern_warnings", [])),
            },
        }
    
    def score(
        self,
        password: str,
        lstm_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate password security score only.
        
        Args:
            password: Password text to score.
            lstm_score: Optional LSTM score (0-100).
        
        Returns:
            Scoring result dictionary with:
            - password: The input password
            - final_score: Overall security score (0-100)
            - rule_score: Rule-based score component
            - lstm_score: LSTM score component (if provided)
            - security_level: Human-readable level
            - feedback: List of improvement suggestions
        """
        password = str(password) if password is not None else ""
        result = self.risk_scorer.score(password, lstm_score)
        
        return {
            "password": password,
            "final_score": result.final_score,
            "rule_score": result.rule_score,
            "lstm_score": result.lstm_score,
            "security_level": result.security_level,
            "feedback": result.feedback,
        }
    
    def explain(self, password: str) -> Dict[str, Any]:
        """
        Get user-friendly explanation and suggestions for a password.
        
        Args:
            password: Password text to explain.
        
        Returns:
            Explanation dictionary with:
            - password: The input password
            - security_level: Assessment level (Güçlü/Orta/Zayıf)
            - assessment: Human-friendly assessment text
            - missing_requirements: List of missing rules
            - pattern_warnings: List of weak pattern warnings
            - suggestions: Actionable improvement suggestions
            - is_strong: Boolean indicating strength
        """
        password = str(password) if password is not None else ""
        return explain_password(password)
    
    def generate(self, length: int = 16) -> Dict[str, Any]:
        """
        Generate a secure password meeting all criteria.
        
        Args:
            length: Desired password length (minimum 8, default 16).
        
        Returns:
            Generated password dictionary with:
            - password: Generated password
            - length: Actual password length
            - weak_patterns: Any detected weak patterns
            - analysis: Quick analysis of generated password
        """
        result = generate_password(length)
        
        # Quick analysis of generated password
        patterns = detect_patterns(result["password"])
        risk_result = self.risk_scorer.score(result["password"])
        
        return {
            **result,
            "patterns": patterns,
            "risk_score": risk_result.final_score,
            "security_level": risk_result.security_level,
            "is_strong": len(patterns) == 0 and risk_result.final_score >= 80,
        }
    
    def generate_and_analyze(self, length: int = 16) -> Dict[str, Any]:
        """
        Generate a secure password and return comprehensive analysis.
        
        Args:
            length: Desired password length (minimum 8, default 16).
        
        Returns:
            Complete analysis of generated password (see analyze() for details).
        """
        generated = generate_password(length)
        return self.analyze(generated["password"])
    
    def batch_analyze(
        self,
        passwords: list[str],
        lstm_scores: Optional[list[Optional[float]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze multiple passwords in batch.
        
        Args:
            passwords: List of passwords to analyze.
            lstm_scores: Optional list of LSTM scores (one per password).
        
        Returns:
            Dictionary with:
            - results: List of analysis results for each password
            - summary: Batch statistics
        """
        if lstm_scores is None:
            lstm_scores = [None] * len(passwords)
        
        if len(passwords) != len(lstm_scores):
            raise ValueError("passwords and lstm_scores must have same length")
        
        results = []
        security_levels = {"Çok Zayıf": 0, "Zayıf": 0, "Orta": 0, "Güçlü": 0, "Çok Güçlü": 0}
        total_score = 0.0
        strong_count = 0
        rules_all_passed_count = 0
        
        for password, lstm_score in zip(passwords, lstm_scores):
            analysis = self.analyze(password, lstm_score)
            results.append(analysis)
            security_levels[analysis["security_level"]] += 1
            total_score += analysis["risk_score"]
            if analysis["is_strong"]:
                strong_count += 1
            if analysis["rules_analysis"]["all_passed"]:
                rules_all_passed_count += 1
        
        return {
            "results": results,
            "summary": {
                "total_analyzed": len(passwords),
                "strong_passwords": strong_count,
                "weak_passwords": len(passwords) - strong_count,
                "rules_all_passed": rules_all_passed_count,
                "average_score": round(total_score / len(passwords), 2) if passwords else 0,
                "security_level_distribution": security_levels,
            },
        }
