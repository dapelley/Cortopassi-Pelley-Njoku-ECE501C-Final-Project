### How to Run Locally

1. **Place `historical_data.csv` and these files** in the same folder.

2. Run:

   python load_data.py
   This creates and populates restaurant_order_recommender.db.

3. Check database health:
    
    python evaluate_db.py

4. Explore queries:
    
    sqlite3 restaurant_order_recommender.db < analysis_queries.sql

5. Run recommendations:
    
    python recommend.py

    Insights You’ll Get
    
        analysis_queries.sql

    A. Top restaurants by average order value

    B. Fastest restaurants by average delivery time

    C. Average dasher load per market (proxy for region congestion)

    D. Dashers vs. delivery-time correlation

    recommend.py

        A. top_value() — finds high-value restaurants

        B. top_fastest() — finds fast delivery performers

