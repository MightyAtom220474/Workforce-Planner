from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
# import plotly.express as px
import plotly.colors as pc

from erlang_utils import calculate_staffing_curve #, calculate_erlang

st.set_page_config(page_title="Erlang C Workforce Planner", layout="wide")

def workforce():

    st.title("Erlang C Workforce Planner")
    st.caption("Calculate staffing requirements and view the staffing curve.")

    with st.sidebar:
        st.header("Inputs")

        transactions = st.number_input(
            "Number of Incoming Calls",
            min_value=0,
            value=100,
            step=1,
            help="The number of incoming calls received within a given time period, typically 30 minutes"
        )
        
        interval = st.slider(
            "In a Time Period Of (seconds)",
            min_value=0,
            max_value=1800,
            value = 1800,
            step=60,
            help="The time period during which the above number of calls was received e.g. 30 minutes = 1800 seconds"
        )

        aht = st.number_input(
            "Average Handling Time (seconds)",
            min_value=1,
            value=180,
            step=1,
            help="Average amount of time take per call"
        )

        asa = st.number_input(
            "Average Speed of Answer Target (seconds)",
            min_value=1,
            max_value=300,
            value=20,
            step=1,
            help="Target for how quickly calls should be answered"
        )

        shrinkage_pct = st.slider(
            "Shrinkage (%)",
            min_value=0,
            max_value=80,
            value=30,
            step=1,
            help="The percentage of paid time that staff are unavailable to answer calls"
        )

        service_level_target = st.slider(
            "Service Level Target",
            min_value=0.0,
            max_value=99.0,
            value=80.0,
            step=0.5,
            help="The percentage of calls that are to be anwswered within the target time set above"
        )

        max_staff = st.number_input(
            "Maximum Staff to Calculate",
            min_value=1,
            value=100,
            step=1,
            help="The maximum number of staff it is possible to have available at any one time"
        )

        run_btn = st.button("Run Calculation", type="primary")

    st.markdown("### What this app does")
    st.write(
        "It calculates the service level achieved at each staffing level and plots the curve against your target."
    )

    if run_btn:
        try:
            df = calculate_staffing_curve(
                transactions=transactions,
                aht=aht,
                asa=asa,
                interval=interval,
                shrinkage=shrinkage_pct / 100.0,
                max_staff_limit=int(max_staff)
            )

            # Find first staffing level that meets or exceeds the target
            meeting_target = df[df["service_level"] >= service_level_target/100]

            if not meeting_target.empty:
                recommended_staff = int(meeting_target.iloc[0]["staff"])
                recommended_service_level = float(meeting_target.iloc[0]["service_level"])
            else:
                recommended_staff = None
                recommended_service_level = None

            # KPI cards
            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Recommended Staffing Level",
                recommended_staff if recommended_staff is not None else "N/A",
            )

            col2.metric(
                "Target Service Level",
                f"{service_level_target}%",
            )

            col3.metric(
                "Recommended Service Level",
                f"{recommended_service_level:.1%}" if recommended_service_level is not None else "N/A",
            )

            col4.metric(
                "Shrinkage",
                f"{shrinkage_pct}%",
            )

            st.subheader("Staffing curve")

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=df["staff"],
                    y=df["service_level_pct"],
                    name="Service level",
                    marker_color=pc.qualitative.Plotly[0],
                    hovertemplate="Staff: %{x}<br>Service level: %{y:.1f}%<extra></extra>",
                )
            )

            fig.add_hline(
                y=service_level_target,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Target ({service_level_target/100:.0%})",
                annotation_position="top left",
            )

            if recommended_staff is not None:
                fig.add_vline(
                    x=recommended_staff,
                    line_dash="dot",
                    line_color="green",
                    annotation_text=f"Recommended staff: {recommended_staff}",
                    annotation_position="top right",
                )

            fig.update_layout(
                xaxis_title="Staff",
                yaxis_title="Service level (%)",
                template="plotly_white",
                bargap=0.15,
                height=550,
                legend_title_text="Legend",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Data Table")
            
            df_display = (
                        df
                        .drop(
                            columns=[
                                "service_level"]
                        ).rename(
                        columns={
                            "staff": "Number of Staff",
                            "service_level_pct": "Service Level (%)",
                            "adjusted_staff_for_shrinkage": "Staff Level incl. Shrinkage",
                        })
                        )

            st.dataframe(df_display, use_container_width=True)
            #st.dataframe(df, use_container_width=True)

            # st.subheader("Input assumptions")
            # st.dataframe(
            #     pd.DataFrame(
            #         [
            #             {
            #                 "transactions": transactions,
            #                 "aht_seconds": aht,
            #                 "asa_seconds": asa,
            #                 "interval_seconds": interval,
            #                 "shrinkage_pct": shrinkage_pct,
            #                 "service_level_target": service_level_target,
            #                 # "max_staff": max_staff,
            #             }
            #         ]
            #     ),
            #     use_container_width=True,
            # )

        except Exception as e:
            st.error(f"Calculation failed: {e}")
            st.exception(e)
    else:
        st.info("Set your inputs in the sidebar, then click Run calculation.")