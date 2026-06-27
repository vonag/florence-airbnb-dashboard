"""
Florence Airbnb Dashboard
Interactive Streamlit + Altair dashboard built on the Inside Airbnb Florence dataset.
"""

import streamlit as st
import pandas as pd
import altair as alt

# ----- Page config -----
st.set_page_config(
    page_title="Florence Airbnb Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Altair: allow more than 5,000 rows
alt.data_transformers.disable_max_rows()


# ----- Data loading -----
@st.cache_data
def load_data():
    df = pd.read_csv("listings.csv")
    # Clean price ("$147.00" -> 147.0)
    df["price"] = (
        df["price"].astype(str).str.replace(r"[$,]", "", regex=True)
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    # Keep just what the dashboard needs
    keep = [
        "name",
        "neighbourhood_cleansed",
        "room_type",
        "price",
        "review_scores_rating",
        "number_of_reviews",
        "latitude",
        "longitude",
        "minimum_nights",
        "accommodates",
    ]
    return df[keep]


df = load_data()


# ----- Header -----
st.title("Florence Airbnb Listings Dashboard")
st.caption(
    "Inside Airbnb data for Florence, Italy. Use the filters in the sidebar to "
    "explore how listings, prices, and ratings vary across neighborhoods and room types."
)


# ----- Sidebar filters -----
st.sidebar.header("Filters")

neighborhoods = sorted(df["neighbourhood_cleansed"].dropna().unique().tolist())
selected_nbhds = st.sidebar.multiselect(
    "Neighborhoods",
    options=neighborhoods,
    default=neighborhoods,
)

room_types = sorted(df["room_type"].dropna().unique().tolist())
selected_rooms = st.sidebar.multiselect(
    "Room types",
    options=room_types,
    default=room_types,
)

price_floor = int(df["price"].min())
price_ceiling = int(df["price"].quantile(0.99))  # ignore extreme outliers in the slider
price_range = st.sidebar.slider(
    "Price range ($/night)",
    min_value=price_floor,
    max_value=price_ceiling,
    value=(price_floor, min(500, price_ceiling)),
)

min_reviews = st.sidebar.slider(
    "Minimum number of reviews",
    min_value=0,
    max_value=int(df["number_of_reviews"].max()),
    value=0,
    step=5,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Filters apply to every chart at once. The scatter plot below also has a "
    "drag-to-select brush that filters the histogram beneath it."
)


# ----- Apply filters -----
filtered = df[
    (df["neighbourhood_cleansed"].isin(selected_nbhds))
    & (df["room_type"].isin(selected_rooms))
    & (df["price"].between(price_range[0], price_range[1]))
    & (df["number_of_reviews"] >= min_reviews)
].copy()


# ----- Top KPI strip -----
k1, k2, k3, k4 = st.columns(4)
k1.metric("Listings shown", f"{len(filtered):,}")
k2.metric(
    "Avg price",
    f"${filtered['price'].mean():.0f}" if len(filtered) else "—",
)
k3.metric(
    "Median price",
    f"${filtered['price'].median():.0f}" if len(filtered) else "—",
)
k4.metric(
    "Avg rating",
    f"{filtered['review_scores_rating'].mean():.2f}"
    if filtered["review_scores_rating"].notna().any()
    else "—",
)

st.divider()

# Bail out early if no rows match
if len(filtered) == 0:
    st.warning("No listings match your filters. Try loosening them.")
    st.stop()


# ===== Row 1: bar + boxplot =====
left, right = st.columns(2)

# Chart 1: listings by neighborhood
bar = (
    alt.Chart(filtered)
    .mark_bar()
    .encode(
        x=alt.X("count():Q", title="Number of listings"),
        y=alt.Y("neighbourhood_cleansed:N", sort="-x", title="Neighborhood"),
        color=alt.Color("neighbourhood_cleansed:N", legend=None),
        tooltip=[
            alt.Tooltip("neighbourhood_cleansed:N", title="Neighborhood"),
            alt.Tooltip("count():Q", title="Listings"),
        ],
    )
    .properties(title="Listings by neighborhood", height=280)
)
left.altair_chart(bar, use_container_width=True)

# Chart 2: price by room type
box = (
    alt.Chart(filtered)
    .mark_boxplot(extent="min-max")
    .encode(
        x=alt.X("room_type:N", title="Room type"),
        y=alt.Y("price:Q", title="Price ($/night)"),
        color=alt.Color("room_type:N", legend=None),
    )
    .properties(title="Price distribution by room type", height=280)
)
right.altair_chart(box, use_container_width=True)


# ===== Row 2: linked scatter + histogram (Altair-native brushing) =====
st.subheader("Price vs. review score")
st.caption(
    "Drag a box across the scatter plot to highlight a price range — the histogram below "
    "updates to show only those listings."
)

brush = alt.selection_interval(encodings=["x"])

scatter_data = filtered.dropna(subset=["review_scores_rating"])

scatter = (
    alt.Chart(scatter_data)
    .mark_circle(opacity=0.45)
    .encode(
        x=alt.X("price:Q", title="Price ($/night)"),
        y=alt.Y(
            "review_scores_rating:Q",
            title="Review score",
            scale=alt.Scale(zero=False),
        ),
        color=alt.condition(brush, "room_type:N", alt.value("lightgray")),
        tooltip=[
            alt.Tooltip("name:N", title="Listing"),
            alt.Tooltip("neighbourhood_cleansed:N", title="Neighborhood"),
            alt.Tooltip("room_type:N", title="Room type"),
            alt.Tooltip("price:Q", title="Price"),
            alt.Tooltip("review_scores_rating:Q", title="Rating"),
        ],
    )
    .add_params(brush)
    .properties(height=320)
)

hist = (
    alt.Chart(scatter_data)
    .mark_bar()
    .encode(
        x=alt.X("price:Q", bin=alt.Bin(maxbins=30), title="Price ($/night)"),
        y=alt.Y("count():Q", title="Selected listings"),
        color=alt.Color("room_type:N", title="Room type"),
    )
    .transform_filter(brush)
    .properties(height=180)
)

st.altair_chart(scatter & hist, use_container_width=True)


# ===== Row 3: map =====
st.subheader("Where are the filtered listings?")
st.map(
    filtered[["latitude", "longitude"]].dropna(),
    size=3,
    zoom=11,
)


# ===== Raw data peek =====
with st.expander("View filtered listings as a table"):
    st.dataframe(
        filtered[
            [
                "name",
                "neighbourhood_cleansed",
                "room_type",
                "price",
                "review_scores_rating",
                "number_of_reviews",
            ]
        ].reset_index(drop=True),
        use_container_width=True,
    )

st.caption("Data source: Inside Airbnb — Florence, Italy.")
