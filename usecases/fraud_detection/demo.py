"""
Fraud Detection Demo -- Run end-to-end analysis on sample transactions.
"""

from usecases.fraud_detection.analyzer import FraudDetector, Transaction

def main():
    print("=" * 70)
    print("HSRAI Fraud Detection System - Demo")
    print("=" * 70)
    
    detector = FraudDetector()
    
    transactions = [
        Transaction(
            tx_id="TX_DEMO_001",
            amount=250.00,
            merchant="LocalGrocery",
            merchant_category="grocery",
            country="US",
            account_id="ACC001",
            timestamp="2026-01-15T10:30:00",
        ),
        Transaction(
            tx_id="TX_DEMO_002",
            amount=15000.00,
            merchant="OnlineShopX",
            merchant_category="electronics",
            country="NG",
            account_id="ACC002",
            timestamp="2026-01-16T02:15:00",
        ),
        Transaction(
            tx_id="TX_DEMO_003",
            amount=8500.00,
            merchant="WireTransferSvc",
            merchant_category="finance",
            country="RU",
            account_id="ACC002",
            timestamp="2026-01-16T02:20:00",
        ),
        Transaction(
            tx_id="TX_DEMO_004",
            amount=50000.00,
            merchant="CryptoExchange",
            merchant_category="crypto",
            country="NG",
            account_id="ACC002",
            timestamp="2026-01-16T02:25:00",
        ),
    ]
    
    results = detector.analyze_batch(transactions)
    
    for r in results:
        print()
        print("-" * 70)
        print(f"Transaction: {r.transaction_id}")
        print(f"  Amount:     ${r.metadata.get('amount', 0):,.2f}")
        print(f"  Merchant:   {r.metadata.get('merchant', 'N/A')}")
        print(f"  Risk Score: {r.risk_score:.3f}")
        print(f"  Risk Level: {r.risk_level.upper()}")
        print("  Risk Factors:")
        for factor in r.risk_factors:
            print(f"    * {factor[1]} (weight: {factor[0]})")
        print("  Recommendations:")
        for rec in r.recommendations:
            print(f"    > {rec}")
        print(f"  Trust Certificate: {r.trust_certificate_id}")
        print(f"  Processing Time:   {r.processing_time_ms:.2f}ms")
    
    print()
    print("=" * 70)
    print("System Summary:")
    summary = detector.get_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("=" * 70)


if __name__ == "__main__":
    main()
