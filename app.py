import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Supply Chain Disruption Monte Carlo', page_icon='🚨', layout='wide')
st.title('🚨 Supply Chain Disruption Simulation')
st.caption('Monte Carlo simulation for inventory, disruption risk, service performance, and cost.')

with st.sidebar:
    st.header('Simulation Inputs')
    normal_supply = st.number_input('Normal weekly supply (units)', 1, 100000, 500, 10, key='normal_supply')
    weekly_demand = st.number_input('Weekly demand (units)', 1, 100000, 450, 10, key='weekly_demand')
    initial_inventory = st.number_input('Initial inventory (units)', 0, 100000, 600, 50, key='initial_inventory')
    st.subheader('Disruption')
    disruption_probability = st.slider('Weekly disruption probability', 0.0, 1.0, 0.10, 0.01, key='disruption_probability')
    disrupted_supply = st.number_input('Supply during disruption (units/week)', 0, 100000, 100, 10, key='disrupted_supply')
    disruption_duration = st.number_input('Disruption duration (weeks)', 1, 52, 2, 1, key='disruption_duration')
    st.subheader('Cost')
    holding_cost = st.number_input('Holding cost ($/unit/week)', 0.0, 100000.0, 2.0, 0.5, key='holding_cost')
    shortage_cost = st.number_input('Shortage cost ($/unit)', 0.0, 100000.0, 15.0, 1.0, key='shortage_cost')
    st.subheader('Monte Carlo')
    weeks = st.number_input('Simulation horizon (weeks)', 4, 104, 12, 1, key='weeks')
    simulations = st.number_input('Number of simulations', 100, 20000, 5000, 500, key='simulations')
    seed = st.number_input('Random seed', 0, 999999, 42, 1, key='seed')
    run = st.button('▶ Run Monte Carlo Simulation', type='primary', use_container_width=True, key='run_main')

if 'run_simulation' not in st.session_state:
    st.session_state.run_simulation = True
if run:
    st.session_state.run_simulation = True

@st.cache_data(show_spinner=False)
def simulate(normal_supply, weekly_demand, initial_inventory, disruption_probability,
             disrupted_supply, disruption_duration, holding_cost, shortage_cost,
             weeks, simulations, seed):
    rng = np.random.default_rng(seed)
    inventory = np.zeros((simulations, weeks + 1))
    supply = np.zeros((simulations, weeks))
    demand = np.zeros((simulations, weeks))
    shortage = np.zeros((simulations, weeks))
    disruption = np.zeros((simulations, weeks), dtype=bool)
    inventory[:, 0] = initial_inventory
    for s in range(simulations):
        active_until = -1
        for t in range(weeks):
            if t > active_until and rng.random() < disruption_probability:
                active_until = min(weeks - 1, t + disruption_duration - 1)
            disrupted = t <= active_until
            disruption[s, t] = disrupted
            supply[s, t] = disrupted_supply if disrupted else normal_supply
            demand[s, t] = rng.poisson(max(0, weekly_demand))
            available = inventory[s, t] + supply[s, t]
            shortage[s, t] = max(0.0, demand[s, t] - available)
            inventory[s, t + 1] = max(0.0, available - demand[s, t])
    avg_inventory = inventory[:, 1:].mean(axis=1)
    total_shortage = shortage.sum(axis=1)
    stockout_weeks = (shortage > 0).sum(axis=1)
    total_holding = avg_inventory * holding_cost * weeks
    total_shortage_cost = total_shortage * shortage_cost
    total_cost = total_holding + total_shortage_cost
    disruption_weeks = disruption.sum(axis=1)
    service_level = np.where(demand.sum(axis=1) > 0, 1 - total_shortage / demand.sum(axis=1), 1.0)
    results = pd.DataFrame({
        'simulation': np.arange(1, simulations + 1),
        'average_inventory': avg_inventory,
        'total_shortage': total_shortage,
        'stockout_weeks': stockout_weeks,
        'service_level': service_level,
        'disruption_weeks': disruption_weeks,
        'holding_cost': total_holding,
        'shortage_cost': total_shortage_cost,
        'total_cost': total_cost,
    })
    return inventory, supply, demand, shortage, disruption, results

if st.session_state.run_simulation:
    inventory, supply, demand, shortage, disruption, results = simulate(
        int(normal_supply), int(weekly_demand), int(initial_inventory), float(disruption_probability),
        int(disrupted_supply), int(disruption_duration), float(holding_cost), float(shortage_cost),
        int(weeks), int(simulations), int(seed))
    labels = [f'Week {i}' for i in range(1, weeks + 1)]
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric('Expected shortage', f"{results.total_shortage.mean():,.1f}")
    c2.metric('Stockout probability', f"{(results.stockout_weeks > 0).mean():.1%}")
    c3.metric('Expected service level', f"{results.service_level.mean():.1%}")
    c4.metric('Expected total cost', f"${results.total_cost.mean():,.0f}")
    c5.metric('Average inventory', f"{results.average_inventory.mean():,.1f}")
    tabs = st.tabs(['📊 Overview','🚨 Risk','📦 Inventory','💰 Cost','📈 Distributions','🔬 Scenarios','📋 Results','🎓 Notes'])

    with tabs[0]:
        avg_inv = inventory[:,1:].mean(axis=0); p10=np.percentile(inventory[:,1:],10,axis=0); p90=np.percentile(inventory[:,1:],90,axis=0)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=labels,y=p90,mode='lines',name='P90',line=dict(width=0)))
        fig.add_trace(go.Scatter(x=labels,y=p10,mode='lines',name='10–90% range',fill='tonexty',line=dict(width=0)))
        fig.add_trace(go.Scatter(x=labels,y=avg_inv,mode='lines+markers',name='Average inventory'))
        fig.update_layout(title='Inventory uncertainty band',xaxis_title='Week',yaxis_title='Units',hovermode='x unified')
        st.plotly_chart(fig,use_container_width=True)
        a,b=st.columns(2)
        with a:
            flow=pd.DataFrame({'Week':labels,'Average supply':supply.mean(0),'Average demand':demand.mean(0)}).melt('Week',var_name='Metric',value_name='Units')
            st.plotly_chart(px.line(flow,x='Week',y='Units',color='Metric',markers=True,title='Average weekly supply versus demand'),use_container_width=True)
        with b:
            st.plotly_chart(px.bar(x=labels,y=(shortage>0).mean(0)*100,labels={'x':'Week','y':'Probability (%)'},title='Probability of shortage by week'),use_container_width=True)

    with tabs[1]:
        a,b=st.columns(2)
        with a:
            st.plotly_chart(px.bar(x=labels,y=disruption.mean(0)*100,labels={'x':'Week','y':'Probability (%)'},title='Probability that each week is disrupted'),use_container_width=True)
        with b:
            st.plotly_chart(px.line(x=labels,y=disruption.mean(0).cumsum(),markers=True,labels={'x':'Week','y':'Expected cumulative disruption-weeks'},title='Cumulative disruption exposure'),use_container_width=True)
        a,b=st.columns(2)
        with a: st.plotly_chart(px.histogram(results,x='disruption_weeks',nbins=weeks+1,title='Distribution of disruption duration'),use_container_width=True)
        with b:
            g=results.groupby('disruption_weeks',as_index=False).agg(avg_shortage=('total_shortage','mean'))
            st.plotly_chart(px.bar(g,x='disruption_weeks',y='avg_shortage',title='Expected shortage by disruption exposure'),use_container_width=True)

    with tabs[2]:
        n=min(10,int(simulations)); sample=pd.DataFrame({'Week':np.tile(np.arange(1,weeks+1),n),'Inventory':inventory[:n,1:].reshape(-1),'Simulation':np.repeat(np.arange(1,n+1),weeks)})
        st.plotly_chart(px.line(sample,x='Week',y='Inventory',color='Simulation',title=f'Inventory paths for {n} sample simulations'),use_container_width=True)
        a,b=st.columns(2)
        with a: st.plotly_chart(px.histogram(x=inventory[:,1:].min(1),nbins=40,title='Distribution of minimum inventory',labels={'x':'Minimum inventory'}),use_container_width=True)
        with b: st.plotly_chart(px.scatter(results.sample(min(len(results),3000),random_state=seed),x='average_inventory',y='total_shortage',color='service_level',title='Average inventory versus shortage'),use_container_width=True)
        a,b=st.columns(2)
        with a: st.plotly_chart(px.line(x=labels,y=inventory[:,1:].mean(0),markers=True,title='Expected inventory by week',labels={'x':'Week','y':'Average inventory'}),use_container_width=True)
        with b: st.plotly_chart(px.bar(x=labels,y=shortage.mean(0),title='Expected shortage by week',labels={'x':'Week','y':'Expected shortage'}),use_container_width=True)

    with tabs[3]:
        a,b=st.columns(2)
        with a:
            cost=pd.DataFrame({'Cost type':['Holding cost','Shortage cost'],'Expected cost':[results.holding_cost.mean(),results.shortage_cost.mean()]})
            st.plotly_chart(px.bar(cost,x='Cost type',y='Expected cost',title='Expected cost decomposition'),use_container_width=True)
        with b: st.plotly_chart(px.histogram(results,x='total_cost',nbins=50,title='Distribution of total cost',labels={'total_cost':'Total cost ($)'}),use_container_width=True)
        a,b=st.columns(2)
        with a: st.plotly_chart(px.scatter(results.sample(min(len(results),3000),random_state=seed),x='total_shortage',y='total_cost',color='disruption_weeks',title='Shortage versus total cost'),use_container_width=True)
        with b: st.dataframe(results[['holding_cost','shortage_cost','total_cost']].describe().T[['mean','50%','90%','95%']].rename(columns={'50%':'median','90%':'p90','95%':'p95'}).style.format('${:,.0f}'),use_container_width=True)

    with tabs[4]:
        a,b=st.columns(2)
        with a: st.plotly_chart(px.histogram(results,x='total_shortage',nbins=50,title='Total shortage distribution'),use_container_width=True)
        with b: st.plotly_chart(px.histogram(results,x='service_level',nbins=50,title='Service-level distribution'),use_container_width=True)
        a,b=st.columns(2)
        with a: st.plotly_chart(px.box(results,y='total_shortage',title='Shortage variability'),use_container_width=True)
        with b: st.plotly_chart(px.box(results,y='total_cost',title='Cost variability'),use_container_width=True)
        a,b=st.columns(2)
        with a: st.plotly_chart(px.histogram(results,x='average_inventory',nbins=50,title='Average inventory distribution'),use_container_width=True)
        with b: st.plotly_chart(px.histogram(results,x='stockout_weeks',nbins=weeks+1,title='Stockout-week distribution'),use_container_width=True)

    with tabs[5]:
        st.write('Compare alternative initial-inventory policies under the same disruption assumptions.')
        scenario_inventory=st.multiselect('Initial inventory scenarios',[300,400,500,600,700,800,1000,1200,1500],default=[400,600,800,1000],key='scenario_initial_inventory')
        scenario_sims=st.slider('Simulations per scenario',100,3000,500,100,key='scenario_simulations')
        if st.button('Run Scenario Analysis',key='run_scenario_analysis'):
            records=[]
            for inv0 in scenario_inventory:
                _,_,_,_,_,r=simulate(int(normal_supply),int(weekly_demand),int(inv0),float(disruption_probability),int(disrupted_supply),int(disruption_duration),float(holding_cost),float(shortage_cost),int(weeks),int(scenario_sims),int(seed+inv0))
                records.append({'Initial inventory':inv0,'Expected shortage':r.total_shortage.mean(),'Stockout probability':(r.stockout_weeks>0).mean(),'Service level':r.service_level.mean(),'Expected cost':r.total_cost.mean(),'Average inventory':r.average_inventory.mean()})
            sdf=pd.DataFrame(records)
            a,b=st.columns(2)
            with a: st.plotly_chart(px.line(sdf,x='Initial inventory',y='Expected shortage',markers=True,title='Initial inventory versus expected shortage'),use_container_width=True)
            with b: st.plotly_chart(px.line(sdf,x='Initial inventory',y='Expected cost',markers=True,title='Initial inventory versus expected total cost'),use_container_width=True)
            a,b=st.columns(2)
            with a: st.plotly_chart(px.line(sdf,x='Initial inventory',y='Service level',markers=True,title='Initial inventory versus service level'),use_container_width=True)
            with b: st.plotly_chart(px.line(sdf,x='Initial inventory',y='Stockout probability',markers=True,title='Initial inventory versus stockout probability'),use_container_width=True)
            st.dataframe(sdf,use_container_width=True)

    with tabs[6]:
        st.download_button('⬇ Download Monte Carlo results (CSV)',results.to_csv(index=False).encode(),file_name='supply_chain_disruption_monte_carlo_results.csv',mime='text/csv',key='download_results')
        st.dataframe(results.head(100),use_container_width=True)
        pct=pd.DataFrame({'Metric':['Total shortage','Total cost','Service level','Average inventory'],'P10':[np.percentile(results.total_shortage,10),np.percentile(results.total_cost,10),np.percentile(results.service_level,10),np.percentile(results.average_inventory,10)],'Median':[np.percentile(results.total_shortage,50),np.percentile(results.total_cost,50),np.percentile(results.service_level,50),np.percentile(results.average_inventory,50)],'P90':[np.percentile(results.total_shortage,90),np.percentile(results.total_cost,90),np.percentile(results.service_level,90),np.percentile(results.average_inventory,90)]})
        st.subheader('Key percentiles'); st.dataframe(pct,use_container_width=True)

    with tabs[7]:
        st.markdown('''### How the model works

1. **Disruption generation:** each week has a specified probability of starting a disruption.
2. **Supply reduction:** disrupted weeks use the reduced supply level.
3. **Demand generation:** weekly demand is generated stochastically using a Poisson distribution around the specified mean.
4. **Inventory update:** beginning inventory plus supply is used to satisfy demand; unmet demand becomes shortage.
5. **Performance:** the model calculates shortage, stockout probability, service level, average inventory, holding cost and shortage cost.
6. **Monte Carlo repetition:** thousands of possible futures create outcome distributions rather than one deterministic answer.

**Managerial question:** not simply “Will a disruption occur?”, but “How does disruption uncertainty change inventory, service, shortage risk and total cost?”''')
        st.warning('Educational model: assumptions should be calibrated with real operational data before production use.')
else:
    st.info('Configure the inputs in the sidebar and click **Run Monte Carlo Simulation**.')
