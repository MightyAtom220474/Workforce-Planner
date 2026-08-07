from __future__ import annotations

import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from erlang_utils import calculate_staffing_curve, calculate_erlang, summarise_result

def workforce():

    st.set_page_config(page_title='Erlang C Workforce Planner', layout='wide')
    st.title('Erlang C Workforce Planner')
    st.caption('Calculate required staffing from transactions, AHT, ASA, interval length, and shrinkage.')

    with st.sidebar:

        st.header("Workload Assumptions")

        transactions = st.number_input(
            "Expected contacts during the period",
            min_value=0,
            value=100,
            step=1,
            help="""
            Enter the number of contacts you expect to receive during the selected planning period.
            This could include phone calls, referrals, appointments, emails or other demand depending on your service.
            """
        )

        aht = st.number_input(
            "Average handling time per contact (seconds)",
            min_value=1,
            value=180,
            step=1,
            help="""
            The average amount of staff time needed to complete each contact.
            Include all activities associated with the contact, such as administration, documentation and follow-up where appropriate.
            """
        )

        asa = st.number_input(
            "Target response time (seconds)",
            min_value=1,
            value=20,
            step=1,
            help="""
            The maximum time a person should wait before their contact is answered.
            For example, entering 20 means the model will calculate the percentage of contacts answered within 20 seconds.
            """
        )

        interval_minutes = st.number_input(
        "Planning period (minutes)",
        min_value=1,
        value=30,
        step=5,
        help="""
        The time period over which the expected contacts will occur.

        Examples:
        • 30 minutes = commonly used for contact centre planning
        • 60 minutes = 1 hour
        • 240 minutes = 4 hours

        For example, if you expect 100 contacts over a 30-minute period,
        enter 100 contacts above and 30 minutes here.
        """
        )

        interval = interval_minutes * 60

        shrinkage_pct = st.slider(
            "Staff unavailable time (%)",
            min_value=0,
            max_value=80,
            value=30,
            step=1,
            help="""
            The percentage of staff time unavailable for handling contacts due to annual leave,
            sickness, training, meetings, supervision, breaks and other non-contact activities.
            """
        )

        service_level_target_pct = st.slider(
            "Performance target (%)",
            min_value=50,
            max_value=99,
            value=80,
            step=1,
            help="""
            The percentage of contacts you would like answered within the target response time.
            For example, 80% means 8 out of every 10 contacts should be answered within the target response time.
            """
        )

        service_level_target = service_level_target_pct / 100

        run_btn = st.button(
            "Calculate staffing requirement",
            type="primary"
        )
    
    st.markdown('### What this app does')
    st.write(
        'It uses your input assumptions to calculate the staffing requirement using the Erlang C Model.'
        )

    if run_btn:
        try:
            result = calculate_erlang(
                transactions=transactions,
                aht=aht,
                asa=asa,
                interval=int(interval),
                shrinkage=shrinkage_pct / 100.0,
                service_level_target=service_level_target
            )

            result_df = pd.DataFrame([result])
            
            curve_df = calculate_staffing_curve(
                                                transactions=transactions,
                                                aht=aht,
                                                asa=asa,
                                                interval=int(interval),
                                                shrinkage=shrinkage_pct / 100
                                            )

            #st.dataframe(result_df, use_container_width=True)
            
            #summary = summarise_result(result)
            
            summary = summarise_result(result)

            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "📋 Staffing Recommendation",
                    "📈 Efficiency Analysis",
                    "⚠️ Risk Analysis",
                    "🔍 What-If Scenarios"
                ]
            )
            
            with tab1:

                st.subheader("Recommended Staffing")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Required Staff",
                    summary.get("positions", "N/A")
                )

                col2.metric(
                    "With Shrinkage",
                    summary.get("positions_with_shrinkage", "N/A")
                    )
                    
                col3.metric(
                    "Service Level",
                    f"{summary.get('service_level', 0) * 100:.1f}%"
                )

                col4.metric(
                    "Occupancy",
                    f"{summary.get('occupancy', 0) * 100:.1f}%"
                )
                
                with st.expander("What is shrinkage?"):
                
                    st.write("""
                    **Shrinkage** represents the proportion of paid staff time that is unavailable for handling contacts or delivering services.

                    Examples of shrinkage include:

                    - Annual leave
                    - Sickness absence
                    - Training and development
                    - Team meetings
                    - Supervision
                    - Breaks
                    - Administrative duties
                    - Other non-contact activities

                    Workforce planning calculations first determine how many staff need to be **available** to meet demand. Shrinkage is then applied to calculate how many staff need to be **employed** to achieve that level of availability.

                    **Example**

                    If 10 staff are required to be available and shrinkage is 30%:

                    ```
                    Required Staff = Available Staff ÷ (1 - Shrinkage)

                    10 ÷ (1 - 0.30)
                    = 14.3
                    ```

                    Therefore, approximately **15 staff would need to be employed** to ensure that 10 staff are available on average.

                    Higher shrinkage percentages increase staffing requirements because a smaller proportion of staff time is available for direct service delivery.
                    """)

                st.divider()

                fig = go.Figure()

                fig.add_trace(
                    go.Bar(
                        x=curve_df["staff"],
                        y=curve_df["service_level_pct"],
                        name="Service Level %",
                        marker_color="#1f77b4"
                    )
                )

                fig.add_hline(
                    y=service_level_target * 100,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Target {service_level_target:.0%}"
                )

                fig.update_layout(
                    title="Service Level by Staffing",
                    xaxis_title="Staff",
                    yaxis_title="Service Level %",
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Full Staffing Curve")

                st.dataframe(
                    curve_df,
                    use_container_width=True
                )
                
            with tab2:

                st.subheader("Marginal Improvement Analysis")
                
                st.info("""
                        This view shows the benefit gained from each additional member of staff.
                        As staffing levels increase, the improvement in service level eventually begins to reduce.
                        Use this tab to identify the point of diminishing returns and determine whether additional staffing provides sufficient operational benefit.
                        """)
                
                fig = px.bar(
                    curve_df,
                    x="staff",
                    y="marginal_gain",
                    labels={
                        "staff": "Staff",
                        "marginal_gain": "Improvement (%)"
                    }
                )

                fig.update_layout(
                    title="Service Level Gain from Each Additional Staff Member"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                sweet_spot_df = curve_df[
                    (curve_df["marginal_gain"] < 1)
                    & (curve_df["service_level_pct"] >= service_level_target_pct)
                ]

                if not sweet_spot_df.empty:

                    sweet_spot = int(
                        sweet_spot_df.iloc[0]["staff"]
                    )

                    st.success(
                        f"Recommended staffing sweet spot: {sweet_spot} staff"
                    )

                st.subheader("Target Achievement Table")

                targets = [70, 80, 85, 90, 95]

                target_results = []

                for target in targets:

                    hit = curve_df[
                        curve_df["service_level_pct"] >= target
                    ]

                    if not hit.empty:

                        target_results.append(
                            {
                                "Target": f"{target}%",
                                "Staff Required":
                                int(hit.iloc[0]["staff"])
                            }
                        )

                st.dataframe(
                    pd.DataFrame(target_results),
                    use_container_width=True
                )
                
            with tab3:

                st.subheader("Occupancy Analysis")
                
                fig = px.line(
                    curve_df,
                    x="staff",
                    y="occupancy_pct",
                    markers=True
                )

                fig.add_hline(
                    y=85,
                    line_color="red",
                    line_dash="dash",
                    annotation_text="85% Occupancy Threshold"
                )

                fig.update_layout(
                    title="Occupancy by Staff Level",
                    yaxis_title="Occupancy %"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                curve_df["risk_zone"] = np.where(
                    curve_df["occupancy_pct"] > 90,
                    "High Risk",
                    np.where(
                        curve_df["occupancy_pct"] > 80,
                        "Medium Risk",
                        "Healthy"
                    )
                )

                st.subheader("Risk Categorisation")
                
                st.info("""
                                    This view highlights the operational risks associated with different staffing levels.
                                    Higher occupancy means staff spend more time continuously handling contacts, which can increase pressure, reduce flexibility and impact resilience.
                                    Use this tab to identify staffing levels that balance performance with workforce wellbeing and sustainability.
                                    """)

                fig = px.scatter(
                                curve_df,
                                x="staff",
                                y="service_level_pct",
                                size="occupancy_pct",
                                color="risk_zone",
                                hover_data=[
                                    "occupancy_pct",
                                    "probability_waiting"
                                ],
                                color_discrete_map={
                                    "Healthy": "green",
                                    "Medium Risk": "orange",
                                    "High Risk": "red"
                                }
                            )

                fig.update_layout(
                    title="Staffing Risk Profile"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.dataframe(
                    curve_df[
                        [
                            "staff",
                            "service_level_pct",
                            "occupancy_pct",
                            "probability_waiting",
                            "risk_zone"
                        ]
                    ],
                    use_container_width=True
                )
                
            with tab4:

                st.subheader("Demand Sensitivity")
                
                st.info("""
                        This chart shows how staffing requirements (taking into account shrinkage) change as demand increases or decreases from the expected level. The baseline scenario (100%) represents the demand values entered into the calculator, while the other scenarios demonstrate the potential impact of lower or higher activity levels.

                        Understanding this relationship helps assess the resilience of the service. For example, if demand were to increase by 10% or 20%, the chart shows how many additional staff may be required to maintain the same service level target. Equally, it can highlight opportunities to redeploy resources during periods of reduced demand.

                        Use this analysis to support business continuity planning, seasonal demand modelling, service redesign discussions, and workforce planning decisions. It provides a simple way to understand the potential staffing implications of changes in activity before they occur.
                        """)

                scenarios = []

                for multiplier in [0.8, 0.9, 1.0, 1.1, 1.2]:

                    scenario_result = calculate_erlang(
                        transactions=transactions * multiplier,
                        aht=aht,
                        asa=asa,
                        interval=int(interval),
                        shrinkage=shrinkage_pct / 100.0,
                        service_level_target=service_level_target
                    )

                    scenario_summary = summarise_result(
                        scenario_result
                    )

                    scenarios.append(
                        {
                            "Demand Scenario":
                                f"{int(multiplier * 100)}%",
                            "Required Staff":
                                scenario_summary.get(
                                    "positions_with_shrinkage",
                                    np.nan
                                )
                        }
                    )

                scenario_df = pd.DataFrame(
                    scenarios
                )

                fig = px.bar(
                    scenario_df,
                    x="Demand Scenario",
                    y="Required Staff",
                    color="Required Staff"
                )

                fig.update_layout(
                    title="Demand Sensitivity Analysis"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.dataframe(
                    scenario_df,
                    use_container_width=True
                )


    #         col1, col2, col3, col4 = st.columns(4)
    #         col1.metric('Required positions', summary.get('positions', 'N/A'))
    #         col2.metric('Positions with shrinkage', summary.get('positions_with_shrinkage', 'N/A'))
    #         col3.metric('Achieved service level', summary.get('service_level', 'N/A'))
    #         col4.metric('Occupancy', summary.get('occupancy', 'N/A'))

    #         st.subheader('Full result')
    #         st.dataframe(pd.DataFrame([result]), use_container_width=True)

    #         st.subheader('Input assumptions')
    #         st.dataframe(
    #             pd.DataFrame([
    #                 {
    #                     'transactions': transactions,
    #                     'aht_seconds': aht,
    #                     'asa_seconds': asa,
    #                     'interval_seconds': interval,
    #                     'shrinkage_pct': shrinkage_pct,
    #                     'service_level_target': service_level_target,
    #                 }
    #             ]),
    #             use_container_width=True,
    #         )

        except Exception as e:
            st.error(f'Calculation failed: {e}')
            st.exception(e)
    else:
        st.info('Set your inputs in the sidebar, then click Run calculation.')
