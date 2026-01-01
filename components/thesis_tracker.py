"""
Thesis Tracker Component
Displays status and health of all 13 theses across 4 layers
"""
import streamlit as st
from typing import Dict, Any, List
from config import THESES


def get_conviction_color(conviction: str) -> str:
    """Get color based on conviction level"""
    colors = {
        "high": "green",
        "medium-high": "blue",
        "medium": "orange",
        "low": "red",
    }
    return colors.get(conviction, "gray")


def get_status_emoji(status: str) -> str:
    """Get emoji based on thesis status"""
    emojis = {
        "active": "🟢",
        "core": "⭐",
        "worldview": "🌍",
        "testing": "🧪",
        "long-term": "🔮",
        "invalidated": "❌",
        "confirmed": "✅",
    }
    return emojis.get(status, "⚪")


def render_thesis_card(thesis_num: int, thesis: Dict[str, Any]) -> None:
    """Render a single thesis card"""
    status_emoji = get_status_emoji(thesis["status"])
    conviction = thesis.get("conviction", "medium")

    with st.expander(f"{status_emoji} Thesis {thesis_num}: {thesis['title']}", expanded=False):
        st.markdown(f"**Core Claim:** {thesis['core_claim']}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Conviction:** " + conviction.title())
            st.markdown(f"**Status:** {thesis['status'].title()}")

        with col2:
            st.markdown(f"**Layer:** {thesis['layer_name']}")

        st.markdown("---")

        st.markdown("**What Confirms It:**")
        for item in thesis.get("confirms", []):
            st.caption(f"✅ {item}")

        st.markdown("**What Refutes It:**")
        for item in thesis.get("refutes", []):
            st.caption(f"❌ {item}")


def render_thesis_layer(layer: int, layer_name: str, theses: Dict[int, Dict]) -> None:
    """Render all theses in a layer"""
    layer_theses = {k: v for k, v in theses.items() if v["layer"] == layer}

    if not layer_theses:
        return

    st.subheader(f"Layer {layer}: {layer_name}")

    # Layer description
    descriptions = {
        1: "Foundational beliefs about how the world works. These inform everything downstream.",
        2: "Theses about specific assets and asset classes. The 'what' to invest in.",
        3: "How markets and infrastructure evolve. The 'how' things work.",
        4: "Business-specific theses. How Reserve Labs wins.",
    }
    st.caption(descriptions.get(layer, ""))

    for thesis_num, thesis in layer_theses.items():
        render_thesis_card(thesis_num, thesis)


def render_thesis_summary() -> None:
    """Render thesis summary statistics"""
    st.subheader("Thesis Summary")

    # Count by status
    status_counts = {}
    conviction_counts = {}
    layer_counts = {}

    for thesis in THESES.values():
        status = thesis["status"]
        conviction = thesis.get("conviction", "medium")
        layer = thesis["layer"]

        status_counts[status] = status_counts.get(status, 0) + 1
        conviction_counts[conviction] = conviction_counts.get(conviction, 0) + 1
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**By Status:**")
        for status, count in sorted(status_counts.items()):
            emoji = get_status_emoji(status)
            st.caption(f"{emoji} {status.title()}: {count}")

    with col2:
        st.markdown("**By Conviction:**")
        for conviction, count in sorted(conviction_counts.items(), reverse=True):
            st.caption(f"• {conviction.title()}: {count}")

    with col3:
        st.markdown("**By Layer:**")
        for layer, count in sorted(layer_counts.items()):
            st.caption(f"• Layer {layer}: {count} theses")


def render_thesis_health_dashboard() -> None:
    """Render overall thesis health dashboard"""
    st.subheader("Thesis Health Overview")

    # Check for any invalidated theses
    invalidated = [t for t in THESES.values() if t["status"] == "invalidated"]
    core_theses = [t for t in THESES.values() if t["status"] == "core"]
    testing_theses = [t for t in THESES.values() if t["status"] == "testing"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Theses", len(THESES))

    with col2:
        health_status = "✅ Healthy" if not invalidated else "❌ Issues"
        st.metric("Health", health_status)

    with col3:
        st.metric("Core Theses", len(core_theses))

    with col4:
        st.metric("Being Tested", len(testing_theses))

    if invalidated:
        st.error("⚠️ Some theses have been invalidated! Review immediately.")
        for thesis in invalidated:
            st.caption(f"❌ {thesis['title']}")


def render_thesis_tracker() -> None:
    """Render the complete thesis tracker page"""
    st.title("Thesis Tracker")
    st.markdown("*Monitoring 13 interconnected theses across 4 layers*")

    # Health dashboard
    render_thesis_health_dashboard()
    st.markdown("---")

    # Summary stats
    render_thesis_summary()
    st.markdown("---")

    # Tabs for each layer
    tab1, tab2, tab3, tab4, tab_all = st.tabs([
        "Layer 1: Macro",
        "Layer 2: Asset",
        "Layer 3: Structure",
        "Layer 4: Business",
        "All Theses"
    ])

    with tab1:
        render_thesis_layer(1, "Macro Worldview", THESES)

    with tab2:
        render_thesis_layer(2, "Asset-Level", THESES)

    with tab3:
        render_thesis_layer(3, "Structural/Infrastructure", THESES)

    with tab4:
        render_thesis_layer(4, "Business (Reserve Labs)", THESES)

    with tab_all:
        st.subheader("All 13 Theses")
        for thesis_num in sorted(THESES.keys()):
            render_thesis_card(thesis_num, THESES[thesis_num])


def render_thesis_dependencies() -> None:
    """Render thesis dependency visualization"""
    st.subheader("Thesis Dependencies")
    st.caption("How theses connect to each other")

    # Simplified dependency map
    st.markdown("""
    ```
    Layer 1 (Macro)         Layer 2 (Asset)         Layer 3 (Structure)    Layer 4 (Business)
    ================        ===============         ===================    ==================

    1. Fiscal Dominance ──┬── 4. ETH as SoV ────┬── 7. Tokenization ≠    11. Institutional
           │              │        │            │      Liquidity ────────── Demand Exists
           │              │        │            │           │
    2. Liquidity ─────────┤        │            ├── 8. Data Primitive ── 12. Data Licensing
       Mechanics          │        │            │           │                  Wedge
           │              │        │            │           │
    3. Speculation ───────┴── 5. BTC/ETH ───────┤── 9. Volatility ───────────┘
       Cycle                  Separation        │      Engines
                              │                 │
                         6. DAT Phases ─────────┴── 10. Regulatory ──── 13. AI/Agentic
                                                        Convergence         Economy
    ```
    """)

    st.info("""
    **Key Dependencies:**
    - Thesis 4 (ETH as SoV) depends on Theses 1-3 (macro backdrop) being correct
    - Thesis 6 (DAT Phases) is the core actionable thesis built on Thesis 4
    - Layer 4 theses are business bets that rely on Layer 3 infrastructure theses
    """)
