import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class RetirementCalculator:
    def __init__(self):
        self.city_costs = {
            "Tier 1 (Mumbai, Delhi, Bangalore)": {
                "rent": 45000, "groceries": 15000, "utilities": 4500,
                "transportation": 8000, "healthcare": 4000, "entertainment": 8000,
                "education_child": 20000, "miscellaneous": 6000
            },
            "Tier 2 (Pune, Jaipur, Coimbatore)": {
                "rent": 28000, "groceries": 10000, "utilities": 3000,
                "transportation": 5000, "healthcare": 2500, "entertainment": 5000,
                "education_child": 12000, "miscellaneous": 4000
            },
            "Tier 3 (Small Cities/Towns)": {
                "rent": 18000, "groceries": 7000, "utilities": 2500,
                "transportation": 3000, "healthcare": 2000, "entertainment": 3000,
                "education_child": 8000, "miscellaneous": 3000
            }
        }

    def calculate_monthly_expenses(self, city_tier, family_size, children_count,
                                 own_house=False, custom_expenses=None, emi=0, parental_cost=0, parental_emergency=0):
        base_costs = self.city_costs[city_tier].copy()

        if own_house:
            base_costs["rent"] = 0

        # Apply custom expenses if provided
        if custom_expenses:
            for category, amount in custom_expenses.items():
                if category in base_costs:
                    base_costs[category] = amount

        # Adjust for family size
        if family_size > 3:
            multiplier = family_size / 3
            base_costs["groceries"] *= multiplier
            base_costs["utilities"] *= multiplier * 0.8
            base_costs["miscellaneous"] *= multiplier * 0.9

        # Children education costs
        base_costs["education_child"] *= children_count

        # Add EMI and parental costs
        total_monthly = sum(base_costs.values()) + emi + parental_cost

        return total_monthly, base_costs, parental_emergency

    def project_future_expenses(self, current_monthly, years_to_retirement,
                              general_inflation=0.07, healthcare_inflation=0.11,
                              education_inflation=0.09):
        general_mult = (1 + general_inflation) ** years_to_retirement
        healthcare_mult = (1 + healthcare_inflation) ** years_to_retirement
        education_mult = (1 + education_inflation) ** years_to_retirement

        general_expenses = current_monthly * 0.7 * general_mult
        healthcare_expenses = current_monthly * 0.15 * healthcare_mult
        education_expenses = current_monthly * 0.15 * education_mult

        return {
            "general": general_expenses,
            "healthcare": healthcare_expenses,
            "education": education_expenses,
            "total": general_expenses + healthcare_expenses + education_expenses
        }

    def calculate_corpus_needed(self, monthly_expenses, withdrawal_rate=0.05):
        annual_expenses = monthly_expenses * 12
        return annual_expenses / withdrawal_rate

    def calculate_sip_required(self, target_corpus, years_to_retirement, expected_return=0.12):
        if years_to_retirement <= 0:
            return target_corpus

        monthly_rate = expected_return / 12
        months = years_to_retirement * 12

        sip_amount = target_corpus * monthly_rate / ((1 + monthly_rate) ** months - 1)
        return sip_amount

    def calculate_corpus_duration(self, initial_corpus, annual_expenses, withdrawal_rate, investment_return):
        """Calculate how many years the corpus will last"""
        corpus = initial_corpus
        years = 0

        while corpus > 0 and years < 50:  # Max 50 years
            # Annual return on corpus
            corpus_return = corpus * investment_return
            corpus += corpus_return

            # Annual withdrawal
            withdrawal = max(annual_expenses * (1.07 ** years), corpus * withdrawal_rate)
            corpus -= withdrawal

            years += 1

            if corpus <= 0:
                break

        return years

def main():
    st.set_page_config(page_title="Retirement Fund Calculator", layout="wide",
                       page_icon="💰")

    st.title("💰 Comprehensive Retirement Fund Calculator")
    st.markdown("### Calculate exactly how much you need for comfortable retirement in India")

    calc = RetirementCalculator()

    # Create columns for layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("📋 Input Parameters")

        # Personal Details
        st.subheader("Personal Details")
        current_age = st.slider("Current Age", 25, 65, 35)
        retirement_age = st.slider("Planned Retirement Age", 35, 70, 60)
        years_to_retirement = retirement_age - current_age

        # Family Details
        st.subheader("Family Details")
        family_size = st.selectbox("Family Size", [1, 2, 3, 4, 5, 6], index=2)
        children_count = st.selectbox("Number of Children", [0, 1, 2, 3, 4], index=1)

        # Dependent Parents
        has_parents = st.checkbox("Dependent Parents?")
        parental_monthly = 0
        parental_emergency_fund = 0
        if has_parents:
            parental_monthly = st.number_input("Monthly Parental Care (₹)", 0, 50000, 8000)
            parental_emergency_fund = st.number_input("Parental Medical Emergency Fund (₹ Lakhs)", 5, 50, 20) * 100000

        # Location & Housing
        st.subheader("Location & Housing")
        city_tier = st.selectbox("City Tier", [
            "Tier 1 (Mumbai, Delhi, Bangalore)",
            "Tier 2 (Pune, Jaipur, Coimbatore)", 
            "Tier 3 (Small Cities/Towns)"
        ], index=1)
        own_house = st.checkbox("Own House (No Rent)")

        # Customizable Expenses
        st.subheader("Customize Monthly Expenses")
        default_costs = calc.city_costs[city_tier]

        custom_rent = st.number_input("Rent (₹)", 0, 50000, default_costs["rent"])
        custom_groceries = st.number_input("Groceries (₹)", 0, 50000, default_costs["groceries"])
        custom_utilities = st.number_input("Utilities (₹)", 0, 20000, default_costs["utilities"])
        custom_transportation = st.number_input("Transportation (₹)", 0, 30000, default_costs["transportation"])
        custom_healthcare = st.number_input("Healthcare (₹)", 0, 20000, default_costs["healthcare"])
        custom_entertainment = st.number_input("Entertainment (₹)", 0, 30000, default_costs["entertainment"])
        custom_education = st.number_input("Education per Child (₹)", 0, 50000, default_costs["education_child"])
        custom_miscellaneous = st.number_input("Miscellaneous (₹)", 0, 20000, default_costs["miscellaneous"])

        # EMI Section
        st.subheader("EMI & Loans")
        monthly_emi = st.number_input("Monthly EMI (₹)", 0, 200000, 0)
        emi_years_remaining = st.number_input("EMI Years Remaining", 0, 30, 0)

        # Current Savings Section - NEW ADDITION
        st.subheader("Current Retirement Savings")
        current_retirement_corpus = st.number_input(
            "Your Current Retirement Corpus (₹)", 
            min_value=0, 
            max_value=100_00_00_000, 
            value=0, 
            step=10000,
            help="Enter the current value of your retirement investments (PPF, EPF, Mutual Funds, etc.)"
        )

        # Financial Assumptions
        st.subheader("Financial Assumptions")
        general_inflation = st.slider("General Inflation (%)", 5.0, 10.0, 7.0, 0.1) / 100
        healthcare_inflation = st.slider("Healthcare Inflation (%)", 8.0, 15.0, 11.0, 0.1) / 100
        education_inflation = st.slider("Education Inflation (%)", 6.0, 12.0, 9.0, 0.1) / 100
        expected_return = st.slider("Expected Portfolio Return (%)", 6.0, 15.0, 10.0, 0.1) / 100
        withdrawal_rate = st.slider("Safe Withdrawal Rate (%)", 3.0, 8.0, 5.0, 0.1) / 100

        # Additional Funds
        st.subheader("Additional Planning")
        emergency_fund = st.number_input("Emergency Fund (₹ Lakhs)", 5, 50, 15) * 100000
        child_education_fund = st.number_input("Higher Education per Child (₹ Lakhs)", 0, 100, 25) * 100000
        child_wedding_fund = st.number_input("Wedding Fund per Child (₹ Lakhs)", 0, 100, 30) * 100000

    with col2:
        st.header("📊 Calculation Results")

        # Prepare custom expenses
        custom_expenses = {
            "rent": custom_rent,
            "groceries": custom_groceries,
            "utilities": custom_utilities,
            "transportation": custom_transportation,
            "healthcare": custom_healthcare,
            "entertainment": custom_entertainment,
            "education_child": custom_education,
            "miscellaneous": custom_miscellaneous
        }

        # If EMI will finish before retirement, adjust it
        emi_during_retirement = monthly_emi if emi_years_remaining > years_to_retirement else 0

        # Calculate current expenses
        monthly_expenses, expense_breakdown, parental_emergency = calc.calculate_monthly_expenses(
            city_tier, family_size, children_count, own_house, custom_expenses, 
            monthly_emi, parental_monthly, parental_emergency_fund
        )

        # Project future expenses (EMI might be finished by then)
        future_monthly_without_emi = monthly_expenses - monthly_emi + emi_during_retirement
        future_expenses = calc.project_future_expenses(
            future_monthly_without_emi, years_to_retirement,
            general_inflation, healthcare_inflation, education_inflation
        )

        # Calculate required corpus
        total_required_corpus = calc.calculate_corpus_needed(
            future_expenses["total"], withdrawal_rate
        )

        # NEW: Calculate future value of current corpus
        future_value_current_corpus = current_retirement_corpus * ((1 + expected_return) ** years_to_retirement)

        # NEW: Calculate remaining corpus needed via SIP
        remaining_corpus_needed = max(total_required_corpus - future_value_current_corpus, 0)

        # Calculate SIP requirements based on remaining corpus needed
        sip_conservative = calc.calculate_sip_required(remaining_corpus_needed, years_to_retirement, 0.08)
        sip_moderate = calc.calculate_sip_required(remaining_corpus_needed, years_to_retirement, 0.10)
        sip_aggressive = calc.calculate_sip_required(remaining_corpus_needed, years_to_retirement, expected_return)

        # Additional funds calculation
        total_child_funds = (child_education_fund + child_wedding_fund) * children_count
        total_additional_funds = emergency_fund + total_child_funds + parental_emergency_fund

        # Calculate corpus duration
        total_corpus_at_retirement = future_value_current_corpus + remaining_corpus_needed
        corpus_years = calc.calculate_corpus_duration(
            total_corpus_at_retirement, future_expenses["total"] * 12, withdrawal_rate, expected_return
        )

        # Display key metrics
        col_metric1, col_metric2, col_metric3 = st.columns(3)

        with col_metric1:
            st.metric("Years to Retirement", f"{years_to_retirement} years")
            st.metric("Current Monthly Expenses", f"₹{monthly_expenses:,.0f}")
            st.metric("Current Annual Expenses", f"₹{monthly_expenses*12:,.0f}")

        with col_metric2:
            st.metric("Future Monthly Expenses", f"₹{future_expenses['total']:,.0f}")
            st.metric("Future Annual Expenses", f"₹{future_expenses['total']*12:,.0f}")
            st.metric("Expense Growth", f"{((future_expenses['total']/future_monthly_without_emi)-1)*100:.1f}%")

        with col_metric3:
            st.metric("Total Required Corpus", f"₹{total_required_corpus/10000000:.2f} Cr")
            st.metric("Additional Funds Needed", f"₹{total_additional_funds/10000000:.2f} Cr")
            st.metric("Grand Total Required", f"₹{(total_required_corpus+total_additional_funds)/10000000:.2f} Cr")

        # NEW: Current Corpus Analysis
        st.subheader("📈 Current Savings Analysis")
        col_savings1, col_savings2, col_savings3 = st.columns(3)

        with col_savings1:
            st.metric("Current Retirement Corpus", f"₹{current_retirement_corpus:,.0f}")
        with col_savings2:
            st.metric("Future Value at Retirement", f"₹{future_value_current_corpus/10000000:.2f} Cr")
        with col_savings3:
            st.metric("Remaining Corpus Needed", f"₹{remaining_corpus_needed/10000000:.2f} Cr")

        # Display corpus sufficiency status
        if remaining_corpus_needed <= 0:
            st.success("🎉 Your current retirement savings will be sufficient! You may not need additional SIP.")
            corpus_surplus = future_value_current_corpus - total_required_corpus
            st.info(f"You'll have a surplus of ₹{corpus_surplus/10000000:.2f} crores at retirement!")
        else:
            st.warning(f"💡 You need to save an additional ₹{remaining_corpus_needed/10000000:.2f} crores through SIP.")

        # Corpus Duration
        st.subheader("Corpus Longevity")
        col_duration1, col_duration2 = st.columns(2)
        with col_duration1:
            st.metric("Total Corpus Will Last", f"{corpus_years} years")
        with col_duration2:
            remaining_months = (corpus_years % 1) * 12
            st.metric("Additional Months", f"{remaining_months:.0f} months")

        # SIP Requirements (Updated to show reduced amounts)
        st.subheader("Monthly SIP Requirements (After Considering Current Corpus)")
        sip_col1, sip_col2, sip_col3 = st.columns(3)

        with sip_col1:
            st.metric("Conservative (8%)", f"₹{sip_conservative:,.0f}")
        with sip_col2:
            st.metric("Moderate (10%)", f"₹{sip_moderate:,.0f}")
        with sip_col3:
            st.metric("Aggressive (12%+)", f"₹{sip_aggressive:,.0f}")

        if current_retirement_corpus > 0:
            st.info(f"💰 SIP amounts are reduced because your current ₹{current_retirement_corpus:,} will grow to ₹{future_value_current_corpus/10000000:.2f} crores by retirement!")

        # EMI Impact Analysis
        if monthly_emi > 0:
            st.subheader("EMI Impact Analysis")
            col_emi1, col_emi2 = st.columns(2)
            with col_emi1:
                st.metric("Current EMI", f"₹{monthly_emi:,}")
                st.metric("EMI Years Remaining", f"{emi_years_remaining} years")
            with col_emi2:
                emi_total = monthly_emi * emi_years_remaining * 12
                st.metric("Total EMI Remaining", f"₹{emi_total:,.0f}")
                if emi_years_remaining <= years_to_retirement:
                    st.success("✅ EMI will finish before retirement")
                else:
                    st.warning("⚠️ EMI continues into retirement")

        # Expense Breakdown Chart
        st.subheader("Current Monthly Expense Breakdown")
        expense_items = list(expense_breakdown.items())
        if monthly_emi > 0:
            expense_items.append(('EMI', monthly_emi))
        if parental_monthly > 0:
            expense_items.append(('Parental Care', parental_monthly))

        # Filter out zero or negative amounts
        expense_items = [(cat, amt) for cat, amt in expense_items if amt > 0]

        # Use expense_items for your DataFrame for the pie chart/Error free
        expense_df = pd.DataFrame(expense_items, columns=['Category', 'Amount'])
        fig_expenses = px.pie(expense_df, values='Amount', names='Category', 
                            title="Monthly Expense Distribution")
        st.plotly_chart(fig_expenses, use_container_width=True)

        # Future Expense Projection Chart
        st.subheader("Future Expense Projection by Category")
        future_df = pd.DataFrame({
            'Category': ['General Expenses', 'Healthcare', 'Education'],
            'Current': [future_monthly_without_emi * 0.7, future_monthly_without_emi * 0.15, future_monthly_without_emi * 0.15],
            'Future': [future_expenses['general'], future_expenses['healthcare'], future_expenses['education']]
        })

        fig_future = go.Figure()
        fig_future.add_trace(go.Bar(name='Current', x=future_df['Category'], y=future_df['Current']))
        fig_future.add_trace(go.Bar(name='Future', x=future_df['Category'], y=future_df['Future']))
        fig_future.update_layout(title='Current vs Future Monthly Expenses by Category',
                               xaxis_title='Category', yaxis_title='Amount (₹)')
        st.plotly_chart(fig_future, use_container_width=True)

        # Corpus Growth Simulation (Updated to show total corpus growth)
        st.subheader("Total Corpus Growth Simulation")
        if years_to_retirement > 0:
            years = np.arange(0, years_to_retirement + 1)
            sip_monthly = sip_aggressive

            # Calculate growth of both current corpus and SIP contributions
            total_corpus_values = []
            current_corpus_values = []
            sip_corpus_values = []

            for year in years:
                # Current corpus growth
                current_corpus_value = current_retirement_corpus * ((1 + expected_return) ** year)
                current_corpus_values.append(current_corpus_value)

                # SIP corpus growth
                if year == 0:
                    sip_corpus_value = 0
                else:
                    months = year * 12
                    monthly_rate = expected_return / 12
                    sip_corpus_value = sip_monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
                sip_corpus_values.append(sip_corpus_value)

                # Total corpus
                total_corpus_values.append(current_corpus_value + sip_corpus_value)

            growth_df = pd.DataFrame({
                'Year': years,
                'Current Corpus Growth': current_corpus_values,
                'SIP Corpus Growth': sip_corpus_values,
                'Total Corpus Value': total_corpus_values
            })

            fig_growth = go.Figure()
            fig_growth.add_trace(go.Scatter(x=growth_df['Year'], y=growth_df['Current Corpus Growth'],
                                          mode='lines', name='Current Corpus Growth',
                                          line=dict(color='blue')))
            fig_growth.add_trace(go.Scatter(x=growth_df['Year'], y=growth_df['SIP Corpus Growth'],
                                          mode='lines', name='SIP Corpus Growth',
                                          line=dict(color='green')))
            fig_growth.add_trace(go.Scatter(x=growth_df['Year'], y=growth_df['Total Corpus Value'],
                                          mode='lines', name='Total Corpus',
                                          line=dict(color='red', width=3)))

            fig_growth.add_hline(y=total_required_corpus, line_dash="dash", 
                                annotation_text=f"Target: ₹{total_required_corpus/10000000:.2f} Cr")

            fig_growth.update_layout(title='Retirement Corpus Growth Over Time',
                                   xaxis_title='Years', yaxis_title='Corpus Value (₹)')
            st.plotly_chart(fig_growth, use_container_width=True)

    # Detailed breakdown tables
    st.header("📋 Detailed Analysis")

    col_table1, col_table2 = st.columns(2)

    with col_table1:
        st.subheader("Current Expense Breakdown")
        all_expenses = expense_breakdown.copy()
        if monthly_emi > 0:
            all_expenses['EMI'] = monthly_emi
        if parental_monthly > 0:
            all_expenses['Parental Care'] = parental_monthly

        expense_display = pd.DataFrame({
            'Category': [cat.replace('_', ' ').title() for cat in all_expenses.keys()],
            'Current Amount': [f"₹{amt:,}" for amt in all_expenses.values()],
            'Percentage': [f"{(amt/monthly_expenses)*100:.1f}%" for amt in all_expenses.values()]
        })
        st.dataframe(expense_display, use_container_width=True)

    with col_table2:
        st.subheader("Additional Funds Required")
        additional_items = [
            ('Emergency Fund', emergency_fund),
            ('Higher Education (Total)', child_education_fund * children_count),
            ('Wedding Fund (Total)', child_wedding_fund * children_count),
        ]

        if parental_emergency_fund > 0:
            additional_items.append(('Parental Medical Emergency', parental_emergency_fund))

        additional_items.append(('Grand Total', total_additional_funds))

        additional_df = pd.DataFrame({
            'Fund Type': [item[0] for item in additional_items],
            'Amount': [f"₹{item[1]/100000:.0f} L" for item in additional_items]
        })
        st.dataframe(additional_df, use_container_width=True)

    # Recommendations (Updated with corpus-specific recommendations)
    st.header("💡 Personalized Recommendations")

    recommendations = []

    if years_to_retirement < 10:
        recommendations.append("⚠️ Less than 10 years to retirement - Consider aggressive saving and delayed retirement")
    elif years_to_retirement < 20:
        recommendations.append("📈 Moderate time horizon - Focus on balanced portfolio with higher equity allocation")
    else:
        recommendations.append("🎯 Good time horizon - Start with aggressive equity portfolio and gradually shift to debt")

    if current_retirement_corpus > 0:
        corpus_percentage = (future_value_current_corpus / total_required_corpus) * 100
        if corpus_percentage >= 100:
            recommendations.append("🎉 Congratulations! Your current corpus will be sufficient for retirement")
        elif corpus_percentage >= 75:
            recommendations.append("✅ You're on track! Current corpus covers majority of retirement needs")
        elif corpus_percentage >= 50:
            recommendations.append("👍 Good progress! Your current corpus covers significant portion of retirement")
        elif corpus_percentage >= 25:
            recommendations.append("📈 You've made a start! Continue building your retirement corpus")
        else:
            recommendations.append("⚡ You need to accelerate retirement savings significantly")
    else:
        recommendations.append("🚀 Start your retirement planning now! Every year of delay increases required SIP")

    if sip_aggressive > monthly_expenses * 0.3:
        recommendations.append("💰 Required SIP is high - Consider increasing retirement age or reducing expenses")

    if own_house:
        recommendations.append("🏠 Owning house significantly reduces retirement corpus requirement")
    else:
        recommendations.append("🏠 Consider buying a house to reduce retirement expenses")

    if city_tier == "Tier 1 (Mumbai, Delhi, Bangalore)":
        recommendations.append("🏙️ Consider retiring in Tier 2/3 cities to reduce corpus requirement by 30-50%")

    if monthly_emi > 0 and emi_years_remaining > years_to_retirement:
        recommendations.append("📉 Try to clear EMI before retirement to reduce post-retirement expenses")

    if has_parents:
        recommendations.append("👴 Factor in increasing healthcare costs for elderly parents - consider separate medical insurance")

    if corpus_years < 25:
        recommendations.append("⏰ Corpus may not last full retirement - consider increasing savings or reducing expenses")

    for rec in recommendations:
        st.info(rec)

if __name__ == "__main__":
    main()
