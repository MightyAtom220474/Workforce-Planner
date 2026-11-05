from __future__ import annotations

import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from erlang_utils import calculate_staffing_curve, calculate_erlang, summarise_result, build_shift_curve, highlight_row, highlight_shift_rows, seconds_to_text, format_duration # calculate_shift_results

def workforce():

    st.set_page_config(page_title='Erlang C Workforce Planner', layout='wide')
    st.title('Erlang C Workforce Planner')
    st.caption('Calculate required staffing levels for your call reponse service')

    with st.sidebar:

        st.header("Workload Assumptions")
        
        mode = st.radio(
                        "Planner Mode",
                        [
                            "Simple Planner",
                            "Advanced Planner"
                        ],
                        horizontal=False
                        )

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
        
        if mode == "Advanced Planner":

            st.divider()

            st.subheader("Advanced Queueing Settings")

            patience_time = st.number_input(
                "Average caller patience (seconds)",
                min_value=10,
                max_value=1800,
                value=120,
                step=10,
                help="""
                How long callers are willing to wait before abandoning.
                """
            )
        
        if mode == "Advanced Planner":

            st.divider()

            st.subheader("Shift Demand")
            
            st.info(
                    """
                    Advanced mode uses peak interval demand rather than total shift volume.

                    Erlang C staffing calculations are based on the busiest planning period,
                    typically 30 minutes.

                    Enter the highest demand expected during a single planning interval for
                    each shift rather than the total number of calls received across the shift.
                    """
                    )

            day_calls = st.number_input(
                "Peak Daytime Call Rate",
                min_value=0,
                value=100,
                help="""
                    Enter the busiest interval demand for the Daytime shift.

                    For example, if the busiest 30-minute period receives 22 calls,
                    enter 22.
                    """
                    )

            evening_calls = st.number_input(
                "Peak Evening Call Rate",
                min_value=0,
                value=80,
                help="""
                    Enter the busiest interval demand for the Evening shift.

                    For example, if the busiest 30-minute period receives 18 calls,
                    enter 18.
                    """
                    )

            night_calls = st.number_input(
                "Peak Nighttime Call Rate",
                min_value=0,
                value=60,
                help="""
                    Enter the busiest interval demand for the Night shift.

                    For example, if the busiest 30-minute period receives 12 calls,
                    enter 12.
                    """
                    )  

        else:

            patience_time = 120

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
                                    service_level_target=service_level_target,
                                    patience_time=patience_time
                                    )


            curve_df = calculate_staffing_curve(
                                                transactions=transactions,
                                                aht=aht,
                                                asa=asa,
                                                interval=int(interval),
                                                shrinkage=shrinkage_pct / 100,
                                                patience_time=patience_time
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
            

            #st.dataframe(result_df, width='stretch')
            
            #summary = summarise_result(result)
            
            summary = summarise_result(result)
            
            if mode == "Advanced Planner":

                day_result = calculate_erlang(
                    transactions=day_calls,
                    aht=aht,
                    asa=asa,
                    interval=int(interval),
                    shrinkage=shrinkage_pct / 100,
                    service_level_target=service_level_target,
                    patience_time=patience_time
                )

                evening_result = calculate_erlang(
                    transactions=evening_calls,
                    aht=aht,
                    asa=asa,
                    interval=int(interval),
                    shrinkage=shrinkage_pct / 100,
                    service_level_target=service_level_target,
                    patience_time=patience_time
                )

                night_result = calculate_erlang(
                    transactions=night_calls,
                    aht=aht,
                    asa=asa,
                    interval=int(interval),
                    shrinkage=shrinkage_pct / 100,
                    service_level_target=service_level_target,
                    patience_time=patience_time
                )

                # shift_df = pd.DataFrame([
                #     {
                #         "Shift": "08:00-16:00",
                #         "Calls": day_calls,
                #         "Required Staff": day_result["positions"],
                #         "With Shrinkage": day_result["positions_with_shrinkage"]
                #     },
                #     {
                #         "Shift": "16:00-00:00",
                #         "Calls": evening_calls,
                #         "Required Staff": evening_result["positions"],
                #         "With Shrinkage": evening_result["positions_with_shrinkage"]
                #     },
                #     {
                #         "Shift": "00:00-08:00",
                #         "Calls": night_calls,
                #         "Required Staff": night_result["positions"],
                #         "With Shrinkage": night_result["positions_with_shrinkage"]
                #     }
                # ])
                
                if mode == "Advanced Planner":

                    day_curve = build_shift_curve(
                        day_calls,
                        aht,
                        asa,
                        int(interval),
                        shrinkage_pct / 100,
                        patience_time
                    )

                    evening_curve = build_shift_curve(
                        evening_calls,
                        aht,
                        asa,
                        int(interval),
                        shrinkage_pct / 100,
                        patience_time
                    )

                    night_curve = build_shift_curve(
                        night_calls,
                        aht,
                        asa,
                        int(interval),
                        shrinkage_pct / 100,
                        patience_time
                    )
                    
                # if mode == "Advanced Planner":

                #     st.write(shift_df)

            tab1, tab2 = st.tabs([
                "📈 Staffing Recommendation",
                "📋 Supporting Data"
                # "⚠️ Risk Analysis",
                # "🔍 What-If Scenarios"
                ])
       
            with tab1:

                st.subheader("Recommended Staffing")
                
                if mode == "Advanced Planner":

                    day_result = calculate_erlang(
                        transactions=day_calls,
                        aht=aht,
                        asa=asa,
                        interval=int(interval),
                        shrinkage=shrinkage_pct / 100,
                        service_level_target=service_level_target,
                        patience_time=patience_time
                    )

                    evening_result = calculate_erlang(
                        transactions=evening_calls,
                        aht=aht,
                        asa=asa,
                        interval=int(interval),
                        shrinkage=shrinkage_pct / 100,
                        service_level_target=service_level_target,
                        patience_time=patience_time
                    )

                    night_result = calculate_erlang(
                        transactions=night_calls,
                        aht=aht,
                        asa=asa,
                        interval=int(interval),
                        shrinkage=shrinkage_pct / 100,
                        service_level_target=service_level_target,
                        patience_time=patience_time
                    )

                if mode == "Simple Planner":
                
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
                
                if mode == "Advanced Planner":

                    st.divider()

                    st.subheader("Shift Staffing Requirements (with shrinkage)")
                    
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

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.metric(
                            "🌅 Daytime Shift",
                            day_result["positions_with_shrinkage"]
                        )

                    with c2:
                        st.metric(
                            "🌆 Evening Shift",
                            evening_result["positions_with_shrinkage"]
                        )

                    with c3:
                        st.metric(
                            "🌙 Night Shift",
                            night_result["positions_with_shrinkage"]
                        )
                        
                    # shift_df = pd.DataFrame(
                    #     [
                    #         {
                    #             "Shift": "Daytime",
                    #             "Calls": day_calls,
                    #             "Required Staff":
                    #                 day_result["positions"],
                    #             "With Shrinkage":
                    #                 day_result["positions_with_shrinkage"]
                    #         },
                    #         {
                    #             "Shift": "Evening",
                    #             "Calls": evening_calls,
                    #             "Required Staff":
                    #                 evening_result["positions"],
                    #             "With Shrinkage":
                    #                 evening_result["positions_with_shrinkage"]
                    #         },
                    #         {
                    #             "Shift": "Night",
                    #             "Calls": night_calls,
                    #             "Required Staff":
                    #                 night_result["positions"],
                    #             "With Shrinkage":
                    #                 night_result["positions_with_shrinkage"]
                    #         }
                    #     ]
                    # )
                    
                    

                st.divider()

                if mode == "Simple Planner":
                
                    fig1 = go.Figure()

                    fig1.add_trace(
                        go.Scatter(
                            x=curve_df["staff_with_shrinkage"],
                            y=curve_df["service_level_pct"],
                            mode="lines+markers",
                            name="Service Level %",
                            line=dict(color="#1f77b4",
                                      width=3
                            ),
                        marker=dict(size=8)
                        )
                    )
                    
                    fig1.add_hline(
                                    y=service_level_target_pct,
                                    line_dash="dash",
                                    line_color="red",
                                    annotation_text=f"Target {service_level_target:.0%}"
                                    )
                
                    fig1.update_layout(
                        title="Service Level by Staffing",
                        xaxis_title="Staff",
                        yaxis_title="Service Level %",
                        height=500
                        )
                    
                    st.plotly_chart(
                                    fig1,
                                    width='stretch'
                                    )
                    
                    st.subheader("Risk Categorisation")
                                    
                    st.info("""
                                        This view highlights the operational risks associated with different staffing levels.
                                        Higher occupancy means staff spend more time continuously handling contacts, which can increase pressure, reduce flexibility and impact resilience.
                                        Use this tab to identify staffing levels that balance performance with workforce wellbeing and sustainability.
                                        """)

                    fig2 = px.scatter(
                                    curve_df,
                                    x="staff_with_shrinkage",
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

                    fig2.update_layout(
                        title="Staffing Risk Profile"
                    )
                    
                    fig2.add_hline(
                                    y=service_level_target_pct,
                                    line_dash="dash",
                                    line_color="red",
                                    annotation_text=f"Target {service_level_target:.0%}"
                                    )

                    st.plotly_chart(
                        fig2,
                        width='stretch'
                    )
                    
                    st.subheader("Occupancy Analysis")
                                    
                    fig3 = px.line(
                        curve_df,
                        x="staff_with_shrinkage",
                        y="occupancy_pct",
                        markers=True
                    )
    
                    fig3.add_hline(
                        y=85,
                        line_color="red",
                        line_dash="dash",
                        annotation_text="85% Occupancy Threshold"
                    )
    
                    fig3.update_layout(
                        title="Occupancy by Staff Level",
                        yaxis_title="Occupancy %"
                    )
    
                    st.plotly_chart(
                        fig3,
                        width='stretch'
                    )
                    
                    recommended_staff = result["positions_with_shrinkage"]
                    
                    scenario_df = curve_df.copy()
    
                    scenario_df = scenario_df[
                        (
                            scenario_df["staff_with_shrinkage"]
                            >= recommended_staff - 5
                        ) &
                        (
                            scenario_df["staff_with_shrinkage"]
                            <= recommended_staff + 5
                        )
                    ]
    
                    recommended_staff = int(
                        summary.get("positions_with_shrinkage", 0)
                    )

                    min_staff = max(
                        1,
                        recommended_staff - 5
                    )

                    max_staff = recommended_staff + 5

                    sensitivity_df = curve_df[
                        (curve_df["staff_with_shrinkage"] >= min_staff)
                        &
                        (curve_df["staff_with_shrinkage"] <= max_staff)
                    ].copy()

                    sensitivity_df = sensitivity_df[
                        [
                            "staff_with_shrinkage",
                            "service_level_pct",
                            "occupancy_pct",
                            "asa_seconds",
                            "abandon_rate_pct"
                        ]
                    ]

                    sensitivity_df.columns = [
                        "Staff",
                        "Service Level %",
                        "Occupancy %",
                        "ASA (Seconds)",
                        "Abandon Rate %"
                    ]

                    styled_df = (
                        sensitivity_df.style
                        .apply(
                            highlight_row,
                            axis=1,
                            recommended_staff=recommended_staff
                        )
                    )
                    
                    sensitivity_df.columns = [
                                            "Staff",
                                            "Service Level %",
                                            "Occupancy %",
                                            "ASA (Seconds)",
                                            "Abandon Rate %"
                                            ]
                    
                    st.subheader(
                                "Staffing Sensitivity Analysis"
                                )
    
                    # st.dataframe(
                    #             sensitivity_df.style.apply(
                    #                 lambda row: [
                    #                     "background-color: #fff3cd"
                    #                     if row["Staff"] == recommended_staff
                    #                     else ""
                    #                     for _ in row
                    #                 ],
                    #                 axis=1
                    #             ),
                    #             width='stretch'
                    #             )
                    
                    styled_df = (
                                scenario_df.style
                                .apply(
                                    highlight_row,
                                    axis=1,
                                    recommended_staff=recommended_staff
                                )
                                )
    
                    
                    st.dataframe(
                                styled_df,
                                width='stretch'
                                )
                    
                    st.success(
                                f"""
                                Recommended staffing level: {recommended_staff} staff
    
                                The yellow highlighted row represents the minimum staffing level
                                required to achieve your target service level.
                                """
                            )

                else:

                    fig4 = go.Figure()

                    fig4.add_trace(
                        go.Scatter(
                            x=day_curve["staff_with_shrinkage"],
                            y=day_curve["service_level_pct"],
                            mode="lines+markers",
                            name="Day Shift",
                            line=dict(color="green", width=3),
                            marker=dict(size=8)
                        )
                    )

                    fig4.add_trace(
                        go.Scatter(
                            x=evening_curve["staff_with_shrinkage"],
                            y=evening_curve["service_level_pct"],
                            mode="lines+markers",
                            name="Evening Shift",
                            line=dict(color="orange", width=3),
                            marker=dict(size=8)
                        )
                    )

                    fig4.add_trace(
                        go.Scatter(
                            x=night_curve["staff_with_shrinkage"],
                            y=night_curve["service_level_pct"],
                            mode="lines+markers",
                            name="Night Shift",
                            line=dict(color="purple", width=3),
                            marker=dict(size=8)
                        )
                    )
                    
                    fig4.add_hline(
                                    y=service_level_target_pct,
                                    line_dash="dash",
                                    line_color="red",
                                    annotation_text=f"Target {service_level_target:.0%}"
                                    )
                
                    fig4.update_layout(
                        title="Service Level by Staffing",
                        xaxis_title="Staff",
                        yaxis_title="Service Level %",
                        height=500
                        )
                    
                    st.plotly_chart(
                                    fig4,
                                    width='stretch'
                                    )

                    st.divider()

                    shift_demand_df = pd.DataFrame([
                        {
                            "Shift": "Day",
                            "Calls": day_calls
                        },
                        {
                            "Shift": "Evening",
                            "Calls": evening_calls
                        },
                        {
                            "Shift": "Night",
                            "Calls": night_calls
                        }
                    ])
                    
                    fig = px.pie(
                        shift_demand_df,
                        names="Shift",
                        values="Calls",
                        hole=0.4
                        )

                    fig.update_layout(
                        title="Call Distribution Across Shifts"
                        )

                    st.plotly_chart(
                        fig,
                        width='stretch'
                        )
                    
                    ##### Get data ready for Staffing Sensitivity Analysis table for shifts
                    
                    day_recommended_staff = int(
                        day_result["positions_with_shrinkage"]
                    )

                    day_sensitivity_df = day_curve[
                        (
                            day_curve["staff_with_shrinkage"]
                            >= day_recommended_staff - 5
                        )
                        &
                        (
                            day_curve["staff_with_shrinkage"]
                            <= day_recommended_staff + 5
                        )
                    ].copy()

                    day_sensitivity_df = day_sensitivity_df[
                        [
                            "staff_with_shrinkage",
                            "service_level_pct",
                            "occupancy_pct",
                            "asa_seconds",
                            "abandon_rate_pct"
                        ]
                    ]

                    day_sensitivity_df.columns = [
                        "Staff",
                        "Service Level %",
                        "Occupancy %",
                        "ASA (Seconds)",
                        "Abandon Rate %"
                    ]
                    
                    evening_recommended_staff = int(
                        evening_result["positions_with_shrinkage"]
                    )

                    evening_sensitivity_df = evening_curve[
                        (
                            evening_curve["staff_with_shrinkage"]
                            >= evening_recommended_staff - 5
                        )
                        &
                        (
                            evening_curve["staff_with_shrinkage"]
                            <= evening_recommended_staff + 5
                        )
                    ].copy()

                    evening_sensitivity_df = evening_sensitivity_df[
                        [
                            "staff_with_shrinkage",
                            "service_level_pct",
                            "occupancy_pct",
                            "asa_seconds",
                            "abandon_rate_pct"
                        ]
                    ]

                    evening_sensitivity_df.columns = [
                        "Staff",
                        "Service Level %",
                        "Occupancy %",
                        "ASA (Seconds)",
                        "Abandon Rate %"
                    ]
                    
                    night_recommended_staff = int(
                        night_result["positions_with_shrinkage"]
                    )

                    night_sensitivity_df = night_curve[
                        (
                            night_curve["staff_with_shrinkage"]
                            >= night_recommended_staff - 5
                        )
                        &
                        (
                            night_curve["staff_with_shrinkage"]
                            <= night_recommended_staff + 5
                        )
                    ].copy()

                    night_sensitivity_df = night_sensitivity_df[
                        [
                            "staff_with_shrinkage",
                            "service_level_pct",
                            "occupancy_pct",
                            "asa_seconds",
                            "abandon_rate_pct"
                        ]
                    ]

                    night_sensitivity_df.columns = [
                        "Staff",
                        "Service Level %",
                        "Occupancy %",
                        "ASA (Seconds)",
                        "Abandon Rate %"
                    ]
                    
                    day_recommended = day_result["positions_with_shrinkage"]
                    evening_recommended = evening_result["positions_with_shrinkage"]
                    night_recommended = night_result["positions_with_shrinkage"]

                    day_df = day_curve.copy()
                    day_df["Shift"] = "Day"

                    evening_df = evening_curve.copy()
                    evening_df["Shift"] = "Evening"

                    night_df = night_curve.copy()
                    night_df["Shift"] = "Night"

                    combined_df = pd.concat(
                        [day_df, evening_df, night_df],
                        ignore_index=True
                    )
                
                    combined_df = combined_df[
                            (
                                ((combined_df["Shift"] == "Day")
                                & (combined_df["staff_with_shrinkage"].between(
                                        day_recommended - 5,
                                        day_recommended + 5
                                    )))
                            )
                            |
                            (
                                ((combined_df["Shift"] == "Evening")
                                & (combined_df["staff_with_shrinkage"].between(
                                        evening_recommended - 5,
                                        evening_recommended + 5
                                    )))
                            )
                            |
                            (
                                ((combined_df["Shift"] == "Night")
                                & (combined_df["staff_with_shrinkage"].between(
                                        night_recommended - 5,
                                        night_recommended + 5
                                    )))
                            )
                        ].copy()
            
                    combined_df = combined_df[
                                                [
                                                    "Shift",
                                                    "staff_with_shrinkage",
                                                    "service_level_pct",
                                                    "occupancy_pct",
                                                    "asa_seconds",
                                                    "abandon_rate_pct"
                                                ]
                                            ]
                    combined_df.columns = [
                        "Shift",
                    "Staff",
                        "Service Level %",
                        "Occupancy %",
                        "ASA (Seconds)",
                        "Abandon Rate %"
                    ]
                    
                    # round so matches with recommended staffing levels for highlighting
                    combined_df["Staff"] = (
                                            combined_df["Staff"]
                                            .round()
                                            .astype(int)
                                            )

                    styled_df = (
                                combined_df.style
                                .apply(
                                    highlight_shift_rows,
                                    axis=1,
                                    day_recommended=day_recommended,
                                    evening_recommended=evening_recommended,
                                    night_recommended=night_recommended
                                )
                                )

                    st.subheader(
                                "Staffing Sensitivity Analysis"
                                )

                    st.dataframe(
                        styled_df,
                        width='stretch'
                    )
                    
                    st.markdown(
                            f"""
                        *Key:*
                        🟩 **Day Shift Recommended Staffing:** {day_recommended}

                        🟨 **Evening Shift Recommended Staffing:** {evening_recommended}

                        🟪 **Night  Recommended Staffing:** {night_recommended}
                        """
                    )
                                                                                                               
            with tab2:

                st.subheader("Supporting Data")
                
                st.info("""
                        This view shows the benefit gained from each additional member of staff.
                        As staffing levels increase, the improvement in service level eventually begins to reduce.
                        Use this tab to identify the point of diminishing returns and determine whether additional staffing provides sufficient operational benefit.
                        """)
                
                if mode == "Advanced Planner":
                    
                    shift_summary_df = pd.DataFrame([
                        {
                            "Shift": "Day (08:00 - 16:00)",
                            "Average calls per hour":
                                round(day_calls * (60 / interval_minutes)),
                            "Total call time per shift":
                                format_duration(day_calls * aht)
                        },
                        {
                            "Shift": "Evening (16:00 - 00:00)",
                            "Average calls per hour":
                                round(evening_calls * (60 / interval_minutes)),
                            "Total call time per shift":
                                format_duration(evening_calls * aht)
                        },
                        {
                            "Shift": "Night (00:00 - 08:00)",
                            "Average calls per hour":
                                round(night_calls * (60 / interval_minutes)),
                            "Total call time per shift":
                                format_duration(night_calls * aht)
                        }
                    ])
                    
                    styled_shift_df = (
                                        shift_summary_df.style
                                        .hide(axis="index")
                                        .set_properties(
                                            **{"text-align": "left"}
                                        )
                                        )
        
                    st.markdown(
                        styled_shift_df.to_html(),
                        unsafe_allow_html=True
                    )
                    
                    combined_df = combined_df[
                        [
                            "Shift",
                            "Staff",
                            "Occupancy %",
                            "ASA (Seconds)",
                            "Abandon Rate %"
                        ]
                    ]
                    
                    combined_df.columns = [
                        "Shift",
                        "Staff on Shift",
                        "Utilisation Rate",
                        "Average Call Answer Time",
                        "Call Abandonment Rate"
                    ]
                    
                    combined_df["Average Call Answer Time"] = (
                        combined_df["Average Call Answer Time"]
                        .apply(format_duration)
                    )

                    combined_df["Utilisation Rate"] = (
                        combined_df["Utilisation Rate"]
                        .round(0)
                        .astype(int)
                        .astype(str)
                        + "%"
                    )

                    combined_df["Call Abandonment Rate"] = (
                        combined_df["Call Abandonment Rate"]
                        .round(0)
                        .astype(int)
                        .astype(str)
                        + "%"
                    )
                    
                    styled_combined_df = (
                                        combined_df.style
                                        .hide(axis="index")
                                        .set_properties(
                                            **{"text-align": "left"}
                                        )
                                        )
        
                    st.markdown(
                        styled_combined_df.to_html(),
                        unsafe_allow_html=True
                    )
                    
                    # shift_comparison = pd.DataFrame([
                    #     {
                    #         "Shift": "Day",
                    #         "Calls": day_calls,
                    #         "Required Staff":
                    #             day_result["positions_with_shrinkage"]
                    #     },
                    #     {
                    #         "Shift": "Evening",
                    #         "Calls": evening_calls,
                    #         "Required Staff":
                    #             evening_result["positions_with_shrinkage"]
                    #     },
                    #     {
                    #         "Shift": "Night",
                    #         "Calls": night_calls,
                    #         "Required Staff":
                    #             night_result["positions_with_shrinkage"]
                    #     }
                    # ])

                    # fig_shift = px.bar(
                    #     shift_comparison,
                    #     x="Shift",
                    #     y="Required Staff",
                    #     text="Required Staff",
                    #     color="Required Staff"
                    # )

                    # st.plotly_chart(
                    #     fig_shift,
                    #     width ='content'
                    # )
                
                # fig = px.bar(
                #     curve_df,
                #     x="staff",
                #     y="marginal_gain",
                #     labels={
                #         "staff": "Staff",
                #         "marginal_gain": "Improvement (%)"
                #     }
                # )

                # fig.update_layout(
                #     title="Service Level Gain from Each Additional Staff Member"
                # )

                # st.plotly_chart(
                #     fig,
                #     width='stretch'
                # )

                # sweet_spot_df = curve_df[
                #     (curve_df["marginal_gain"] < 1)
                #     & (curve_df["service_level_pct"] >= service_level_target_pct)
                # ]

                # if not sweet_spot_df.empty:

                #     sweet_spot = int(
                #         sweet_spot_df.iloc[0]["staff"]
                #     )

                #     st.success(
                #         f"Recommended staffing sweet spot: {sweet_spot} staff"
                #     )

                # st.subheader("Target Achievement Table")

                # targets = [70, 80, 85, 90, 95]

                # target_results = []

                # for target in targets:

                #     hit = curve_df[
                #         curve_df["service_level_pct"] >= target
                #     ]

                #     if not hit.empty:

                #         target_results.append(
                #             {
                #                 "Target": f"{target}%",
                #                 "Staff Required":
                #                 int(hit.iloc[0]["staff"])
                #             }
                #         )

                # st.dataframe(
                #     pd.DataFrame(target_results),
                #     width='stretch'
                # )
                
                else:
                    
                    avg_calls_per_hour = transactions * (60 / interval_minutes)

                    total_call_seconds = transactions * aht

                    hours = int(total_call_seconds // 3600)
                    minutes = int((total_call_seconds % 3600) // 60)
                    
                    
                    summary_df = pd.DataFrame(
                        [{
                            "Planning Period": f"{interval_minutes} minutes",
                            "Average calls per hour": round(avg_calls_per_hour),
                            "Total workload": f"{hours} hours {minutes} minutes"
                        }]
                    )
                    
                    styled_summary_df = (
                                summary_df.style
                                .hide(axis="index")
                                .set_properties(
                                    **{"text-align": "left"}
                                )
                                )

                    st.markdown(
                        styled_summary_df.to_html(),
                        unsafe_allow_html=True
                    )
                    
                    # re-use sensitivity_df from earlier
                    
                    display_df = sensitivity_df.copy()
                    
                    display_df = display_df[
                                            [
                                            "Staff",
                                            "Occupancy %",
                                            "ASA (Seconds)",
                                            "Abandon Rate %"
                                            ]
                                            ]

                    display_df.columns = [
                                        "Staff on Shift",
                                        "Utilisation Rate",
                                        "Average Call Answer Time",
                                        "Call Abandonment Rate"
                                        ]
                    
                    display_df["Staff on Shift"] = (
                            display_df["Staff on Shift"]
                            .round()
                            .astype(int)
                        )

                    display_df["Average Call Answer Time"] = (
                        display_df["Average Call Answer Time"]
                        .apply(format_duration)
                    )

                    display_df["Utilisation Rate"] = (
                        display_df["Utilisation Rate"]
                        .round(0)
                        .astype(int)
                        .astype(str)
                        + "%"
                    )

                    display_df["Call Abandonment Rate"] = (
                        display_df["Call Abandonment Rate"]
                        .round(0)
                        .astype(int)
                        .astype(str)
                        + "%"
                    )
                    
                    styled_df = (
                                display_df.style
                                .hide(axis="index")
                                .set_properties(
                                    **{"text-align": "left"}
                                )
                                )

                    st.markdown(
                        styled_df.to_html(),
                        unsafe_allow_html=True
                    )
                
            # with tab3:

            #     st.subheader("Occupancy Analysis")
                
            #     fig = px.line(
            #         curve_df,
            #         x="staff",
            #         y="occupancy_pct",
            #         markers=True
            #     )

            #     fig.add_hline(
            #         y=85,
            #         line_color="red",
            #         line_dash="dash",
            #         annotation_text="85% Occupancy Threshold"
            #     )

            #     fig.update_layout(
            #         title="Occupancy by Staff Level",
            #         yaxis_title="Occupancy %"
            #     )

            #     st.plotly_chart(
            #         fig,
            #         width='stretch'
            #     )

            #     curve_df["risk_zone"] = np.where(
            #         curve_df["occupancy_pct"] > 90,
            #         "High Risk",
            #         np.where(
            #             curve_df["occupancy_pct"] > 80,
            #             "Medium Risk",
            #             "Healthy"
            #         )
            #     )

            #     st.subheader("Risk Categorisation")
                
            #     st.info("""
            #                         This view highlights the operational risks associated with different staffing levels.
            #                         Higher occupancy means staff spend more time continuously handling contacts, which can increase pressure, reduce flexibility and impact resilience.
            #                         Use this tab to identify staffing levels that balance performance with workforce wellbeing and sustainability.
            #                         """)

            #     fig = px.scatter(
            #                     curve_df,
            #                     x="staff",
            #                     y="service_level_pct",
            #                     size="occupancy_pct",
            #                     color="risk_zone",
            #                     hover_data=[
            #                         "occupancy_pct",
            #                         "probability_waiting"
            #                     ],
            #                     color_discrete_map={
            #                         "Healthy": "green",
            #                         "Medium Risk": "orange",
            #                         "High Risk": "red"
            #                     }
            #                 )

            #     fig.update_layout(
            #         title="Staffing Risk Profile"
            #     )

            #     st.plotly_chart(
            #         fig,
            #         width='stretch'
            #     )
                
            #     st.subheader(
            #         "Abandonment Analysis"
            #     )

            #     fig = px.line(
            #         curve_df,
            #         x="staff",
            #         y="abandon_rate_pct",
            #         markers=True
            #     )

            #     fig.update_layout(
            #         title="Abandonment Rate by Staffing Level",
            #         yaxis_title="Abandonment %"
            #     )

            #     st.plotly_chart(
            #         fig,
            #         width='stretch'
            #     )

            #     st.dataframe(
            #         curve_df[
            #             [
            #                 "staff",
            #                 "service_level_pct",
            #                 "occupancy_pct",
            #                 "probability_waiting",
            #                 "risk_zone"
            #             ]
            #         ],
            #         width='stretch'
            #     )
                
            #     st.subheader("Staffing Sensitivity Analysis")

            #     recommended_staff = int(
            #         summary.get("positions", 0)
            #     )

            #     min_staff = max(
            #         1,
            #         recommended_staff - 5
            #     )

            #     max_staff = recommended_staff + 5

            #     sensitivity_df = curve_df[
            #         (curve_df["staff"] >= min_staff)
            #         &
            #         (curve_df["staff"] <= max_staff)
            #     ].copy()
                                
            # with tab4:

            #     st.subheader("Demand Sensitivity")
                
            #     st.info("""
            #             This chart shows how staffing requirements (taking into account shrinkage) change as demand increases or decreases from the expected level. The baseline scenario (100%) represents the demand values entered into the calculator, while the other scenarios demonstrate the potential impact of lower or higher activity levels.

            #             Understanding this relationship helps assess the resilience of the service. For example, if demand were to increase by 10% or 20%, the chart shows how many additional staff may be required to maintain the same service level target. Equally, it can highlight opportunities to redeploy resources during periods of reduced demand.

            #             Use this analysis to support business continuity planning, seasonal demand modelling, service redesign discussions, and workforce planning decisions. It provides a simple way to understand the potential staffing implications of changes in activity before they occur.
            #             """)

            #     scenarios = []

            #     for multiplier in [0.8, 0.9, 1.0, 1.1, 1.2]:

            #         scenario_result = calculate_erlang(
            #             transactions=transactions * multiplier,
            #             aht=aht,
            #             asa=asa,
            #             interval=int(interval),
            #             shrinkage=shrinkage_pct / 100.0,
            #             service_level_target=service_level_target,
            #             patience_time=patience_time
            #         )

            #         scenario_summary = summarise_result(
            #             scenario_result
            #         )

            #         scenarios.append(
            #             {
            #                 "Demand Scenario":
            #                     f"{int(multiplier * 100)}%",
            #                 "Required Staff":
            #                     scenario_summary.get(
            #                         "positions_with_shrinkage",
            #                         np.nan
            #                     )
            #             }
            #         )

            #     scenario_df = pd.DataFrame(
            #         scenarios
            #     )

            #     fig = px.bar(
            #         scenario_df,
            #         x="Demand Scenario",
            #         y="Required Staff",
            #         color="Required Staff"
            #     )

            #     fig.update_layout(
            #         title="Demand Sensitivity Analysis"
            #     )

            #     st.plotly_chart(
            #         fig,
            #         width='stretch'
            #     )

            #     st.dataframe(
            #         scenario_df,
            #         width='stretch'
            #     )
            
            # if mode == "Advanced Planner":

            #     with tab5:
                    
            #         st.subheader("Shift Staffing Requirements")

            #         st.dataframe(
            #             shift_df,
            #             width='stretch'
            #         )

            #         st.subheader(
            #             "Advanced Queueing Metrics"
            #         )

            #         st.dataframe(
            #             pd.DataFrame([
            #                 {
            #                     "Metric": "ASA",
            #                     "Value": f"{summary.get('actual_asa',0):.1f}s"
            #                 },
            #                 {
            #                     "Metric": "Answered Immediately",
            #                     "Value": f"{summary.get('immediate_answer_rate',0)*100:.1f}%"
            #                 },
            #                 {
            #                     "Metric": "Abandon Rate",
            #                     "Value": f"{summary.get('abandon_rate',0)*100:.2f}%"
            #                 }
            #             ]),
            #             width='stretch'
            #         )
                    
            #         if mode == "Advanced Planner":

            #             st.subheader(
            #                 "Demand Distribution By Shift"
            #             )

            #             shift_demand_df = pd.DataFrame([
            #                 {
            #                     "Shift": "Day",
            #                     "Calls": day_calls
            #                 },
            #                 {
            #                     "Shift": "Evening",
            #                     "Calls": evening_calls
            #                 },
            #                 {
            #                     "Shift": "Night",
            #                     "Calls": night_calls
            #                 }
            #             ])
                        
            #             fig = px.pie(
            #                 shift_demand_df,
            #                 names="Shift",
            #                 values="Calls",
            #                 hole=0.4
            #                 )

            #             fig.update_layout(
            #                 title="Call Distribution Across Shifts"
            #                 )

            #             st.plotly_chart(
            #                 fig,
            #                 width='stretch'
            #                 )

    #         col1, col2, col3, col4 = st.columns(4)
    #         col1.metric('Required positions', summary.get('positions', 'N/A'))
    #         col2.metric('Positions with shrinkage', summary.get('positions_with_shrinkage', 'N/A'))
    #         col3.metric('Achieved service level', summary.get('service_level', 'N/A'))
    #         col4.metric('Occupancy', summary.get('occupancy', 'N/A'))

    #         st.subheader('Full result')
    #         st.dataframe(pd.DataFrame([result]), width='stretch')

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
    #             width='stretch',
    #         )

        except Exception as e:
            st.error(f'Calculation failed: {e}')
            st.exception(e)
    else:
        st.info('Set your inputs in the sidebar, then click Run calculation.')
