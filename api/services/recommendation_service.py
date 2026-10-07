import pandas as pd
from recommendation_system.recommend import recommend
from api.schemas.recommendation import RecommendationData, RecommendationItemData
from api.utils.errors import InvalidInputError

def get_user_recommendations(
    user_id: str,
    n: int = 10,
    method: str = "hybrid",
    exclude_purchased: bool = True
) -> RecommendationData:
    """Generate recommendations for a user via recommendation_system package."""
    allowed_methods = {"hybrid", "collaborative", "content", "popular"}
    method_clean = str(method).lower()
    if method_clean not in allowed_methods:
        raise InvalidInputError(f"Invalid recommendation method '{method}'. Allowed methods: {allowed_methods}")

    if n < 1 or n > 100:
        raise InvalidInputError("Recommendation count 'n' must be between 1 and 100.")

    # Call recommendation_system engine
    recs_df = recommend(
        user_id=str(user_id),
        n=n,
        method=method_clean,
        exclude_purchased=exclude_purchased
    )

    items = []
    if not recs_df.empty:
        for _, row in recs_df.iterrows():
            items.append(RecommendationItemData(
                product_id=str(row.get("product_id")),
                score=round(float(row.get("recommendation_score", row.get("score", 0.0))), 4),
                product_name=str(row.get("product_name")) if "product_name" in row and pd.notna(row["product_name"]) else None,
                category=str(row.get("category")) if "category" in row and pd.notna(row["category"]) else None
            ))

    return RecommendationData(
        user_id=str(user_id),
        method=method_clean,
        recommendations=items
    )
