import streamlit as st
import pandas as pd
import plotly.express as px

# function to sort alpha first then numeric values
@st.cache_data
def custom_sort(item):
    if item.isdigit():
        return (float('inf'), int(item))
    else:
        return (0, item)

# display title
st.title('Toric Optic Metrology')

# excel filename
file = 'Toric_Optic_Metrology_Backend_dev_2.xlsx'

# read in excel file
df = pd.read_excel(file, sheet_name='Sheet1')

# display dataframe that shows the Part_Number and its corresponding Part_Description
st.subheader('Part Number and Part Description')
st.dataframe(df[['Part_Number', 'Part_Description']].drop_duplicates().sort_values('Part_Number'), width=2000)

# create empty list to store Part_Number
part_number = []

# loop through dataframe and append unique Part_Number to list
for i in df['Part_Number'].unique():
    part_number.append(i)

# have a sidebar to select the Part_Number
part_number = st.sidebar.selectbox('Part Number:', ['Select Part Number'] + sorted(part_number, key=custom_sort))

# check if Part_Number is selected
if part_number != 'Select Part Number':             # NOTE - selection of Part_Number ###############################################################################################
    # display subheader
    # filter dataframe based on Part_Number
    df_filtered = df[df['Part_Number'] == part_number]
    part_description = df_filtered['Part_Description'].unique()[0]
    st.subheader(f'{part_number}: {part_description}')

    # FIXME - add new attribute 'cylinder_diopter_stability' based on the following conditions
    # if Part_Number selected includes PRD11340, PRD11504, PRD11566, PRD11601, PRD11602, PRD11505, PRD11506, PRD11582, PRD11583 then include a new attribte called 'cylinder_diopter_stability'
    if part_number in ['PRD11340', 'PRD11504', 'PRD11566', 'PRD11601', 'PRD11602', 'PRD11505', 'PRD11506', 'PRD11582', 'PRD11583']:
        # create a new column 'cylinder_diopter_stability' based on the following conditions
        df_filtered['cylinder_diopter_stability'] = df_filtered['Attribute_Value'].apply(lambda x: 'Stable' if x <= 0.5 else 'Unstable')

    # create empty list to store Lot_Number
    lot_number = []

    # loop through filtered dataframe and append unique Lot_Number to list
    for i in df_filtered['Lot_Number'].unique():
        lot_number.append(i)

    # add an option to select all lot numbers
    lot_number.append('All')

    # have a sidebar to multiselect the Lot_Number
    lot_number = st.sidebar.multiselect('Lot Number:', sorted(lot_number, key=custom_sort))

    if 'All' in lot_number:                         # NOTE - selection of Lot_Number ###############################################################################################    
        st.markdown('All Lot Numbers are Selected')

        # create empty list to store attribute numbers
        attribute_number = []
        # loop through filtered dataframe and append unique Attribute_Number to list
        for i in df_filtered['Attribute_Number'].unique():
            attribute_number.append(i)

        # add an option to select all attribute numbers
        attribute_number.append('All')

        # display a dataframe that shows the Attribute_Number and its corresponding Attribute_Description
        st.subheader('Attribute Number and Attribute Description')
        st.dataframe(df_filtered[['Attribute_Number', 'Attribute_Description']].drop_duplicates().sort_values('Attribute_Number'), width=2000)

        # have a sidebar to multiselect the Attribute_Number
        attribute_number = st.sidebar.multiselect('Attribute Number:', sorted(attribute_number, key=custom_sort))

        if 'All' in attribute_number:                   # NOTE - selection of Attribute_Number #######################################################################################
            st.markdown('All Attribute Numbers are Selected')

            # NOTE: display filtered dataframe
            # st.dataframe(df_filtered, width=2000)

            # create checkbox to display summary statistics
            summary = st.checkbox('Display Summary Statistics')

            # if checkbox is selected, display summary statistics for the filtered dataframe
            if summary:
                st.subheader('Summary Statistics')
                st.markdown('**Summary Statistics for All Lot Numbers**')
                # create a dataframe to display summary statistics for attribute_number
                df_summary = df_filtered.groupby(['Attribute_Number']).agg({'Attribute_Value': ['count', 'mean', 'std', 'min', 'max']})
                # rename columns
                df_summary.columns = ['Count', 'Mean', 'Standard Deviation', 'Minimum', 'Maximum']
                # sort df_summary by Attribute_Number
                df_summary = df_summary.sort_index()
                # display summary statistics dataframe
                st.dataframe(df_summary, width=2000)

                # create checkbox to plot the std of each attribute number
                plot_std = st.checkbox('Plot Standard Deviation')

                # if checkbox is selected, display scatter plot for the std of each attribute number
                if plot_std:
                    # create Plotly scatter plot
                    fig = px.scatter(df_summary, x=df_summary.index, y='Standard Deviation', title='Standard Deviation for All Attribute Numbers in All of Lot Numbers')
                    fig.update_layout(xaxis_tickangle=-90)
                    fig.update_xaxes(type='category', dtick=1)
                    fig.update_traces(mode='lines+markers', line=dict(color='blue'), marker=dict(color='blue'))
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)

            # create checkbox to display plot
            plot = st.checkbox('Display Plot')

            # if checkbox is selected and attribute_number is not empty, iterate through all the selected Attribute_Number and display Plotly plot for each Attribute_Number
            if plot and 'All' in attribute_number:          # NOTE - selection of Plot ###############################################################################################
                for i in df_filtered['Attribute_Number'].unique():
                    df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                    # create Plotly scatter plot
                    fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                    labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                    title='Plot for Attribute Number: ' + str(i))
                    # rotate Lot_Number labels by 90 degrees
                    fig.update_layout(xaxis_tickangle=-90)
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)
            
            elif plot and attribute_number:                 # NOTE - selection of Plot for selected Attribute_Number ###################################################################
                    for i in attribute_number:
                        df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                        # create Plotly scatter plot
                        fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                        labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                        title='Plot for Attribute Number: ' + str(i))
                        # rotate Lot_Number labels by 90 degrees
                        fig.update_layout(xaxis_tickangle=-90)
                        # display Plotly plot using Streamlit
                        st.plotly_chart(fig)
            # else:
            #     # display message to select Attribute_Number
            #     st.info('Please select Attribute Number to display plot')

        # check if Attribute_Number is selected
        elif attribute_number:                              # NOTE - selection of Attribute_Number #######################################################################################
            # display subheader
            selected_attributes = ', '.join(attribute_number)
            st.markdown(f'<h3 style="font-size: 16px;">Attribute Number(s): {selected_attributes}</h3>', unsafe_allow_html=True)
            # filter dataframe based on Attribute_Number
            df_filtered = df_filtered[df_filtered['Attribute_Number'].isin(attribute_number)]

            # NOTE: display filtered dataframe
            # st.dataframe(df_filtered, width=2000)

            # create checkbox to display summary statistics
            summary = st.checkbox('Display Summary Statistics')

            # if checkbox is selected, display summary statistics for the filtered dataframe
            if summary:
                st.subheader('Summary Statistics')
                st.markdown('**Summary Statistics for All Lot Numbers**')
                # create a dataframe to display summary statistics for attribute_number
                df_summary = df_filtered.groupby(['Attribute_Number']).agg({'Attribute_Value': ['count', 'mean', 'std', 'min', 'max']})
                # rename columns
                df_summary.columns = ['Count', 'Mean', 'Standard Deviation', 'Minimum', 'Maximum']
                # sort df_summary by Attribute_Number
                df_summary = df_summary.sort_index()
                # display summary statistics dataframe
                st.dataframe(df_summary, width=2000)

                # create checkbox to plot the std of each attribute number
                plot_std = st.checkbox('Plot Standard Deviation')

                # if checkbox is selected, display scatter plot for the std of each attribute number
                if plot_std:
                    # create Plotly scatter plot
                    fig = px.scatter(df_summary, x=df_summary.index, y='Standard Deviation', title=f'Standard Deviation for Attribute Number(s): {selected_attributes}')
                    fig.update_layout(xaxis_tickangle=-90)
                    fig.update_xaxes(type='category', dtick=1)
                    fig.update_traces(mode='lines+markers', line=dict(color='blue'), marker=dict(color='blue'))
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)

            # create checkbox to display plot
            plot = st.checkbox('Display Plot')

            # if checkbox is selected and attribute_number is not empty, iterate through all the selected Attribute_Number and display Plotly plot for each Attribute_Number
            if plot and 'All' in attribute_number:              # NOTE - selection of Plot ###############################################################################################
                for i in df_filtered['Attribute_Number'].unique():
                    df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                    # create Plotly scatter plot
                    fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                    labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                    title='Plot for Attribute Number: ' + str(i))
                    # rotate Lot_Number labels by 90 degrees
                    fig.update_layout(xaxis_tickangle=-90)
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)
            
            elif plot and attribute_number:                     # NOTE - selection of Plot for selected Attribute_Number ###################################################################
                    for i in attribute_number:
                        df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                        # create Plotly scatter plot
                        fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                        labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                        title='Plot for Attribute Number: ' + str(i))
                        # rotate Lot_Number labels by 90 degrees
                        fig.update_layout(xaxis_tickangle=-90)
                        # display Plotly plot using Streamlit
                        st.plotly_chart(fig)
            # else:
            #     # display message to select Attribute_Number
            #     st.info('Please select Attribute Number to display plot')
        else:
            # display message to select Attribute_Number
            st.info('Please select Attribute Number')

    # check if Lot_Number is selected
    elif lot_number:                                             # NOTE - selection of Lot_Number #######################################################################################
        # display subheader
        st.markdown('<h3 style="font-size: 16px;">Lot Number: ' + str(lot_number) + '</h3>', unsafe_allow_html=True)
        # filter dataframe based on Lot_Number
        df_filtered = df_filtered[df_filtered['Lot_Number'].isin(lot_number)]

        # create empty list to store Attribute_Number
        attribute_number = []
        # loop through filtered dataframe and append unique Attribute_Number to list
        for i in df_filtered['Attribute_Number'].unique():
            attribute_number.append(i)

        # add an option to select all attribute numbers
        attribute_number.append('All')

        # display a dataframe that shows the Attribute_Number and its corresponding Attribute_Description
        st.subheader('Attribute Number and Attribute Description')
        st.dataframe(df_filtered[['Attribute_Number', 'Attribute_Description']].drop_duplicates().sort_values('Attribute_Number'), width=2000)

        # have a sidebar to multiselect the Attribute_Number
        attribute_number = st.sidebar.multiselect('Attribute Number:', sorted(attribute_number, key=custom_sort))

        if 'All' in attribute_number:                             # NOTE - selection of Attribute_Number ###################################################################################
            st.markdown('All Attribute Numbers are Selected')

            # NOTE: display filtered dataframe
            # st.dataframe(df_filtered, width=2000)

            # create checkbox to display summary statistics
            summary = st.checkbox('Display Summary Statistics')

            # if checkbox is selected, display summary statistics for the filtered dataframe
            if summary:
                st.subheader('Summary Statistics')
                st.markdown('**Summary Statistics for All Lot Numbers**')
                # create a dataframe to display summary statistics for attribute_number
                df_summary = df_filtered.groupby(['Attribute_Number']).agg({'Attribute_Value': ['count', 'mean', 'std', 'min', 'max']})
                # rename columns
                df_summary.columns = ['Count', 'Mean', 'Standard Deviation', 'Minimum', 'Maximum']
                # sort df_summary by Attribute_Number
                df_summary = df_summary.sort_index()
                # display summary statistics dataframe
                st.dataframe(df_summary, width=2000)

                # create checkbox to plot the std of each attribute number
                plot_std = st.checkbox('Plot Standard Deviation')

                # if checkbox is selected, display scatter plot for the std of each attribute number
                if plot_std:
                    # create Plotly scatter plot
                    fig = px.scatter(df_summary, x=df_summary.index, y='Standard Deviation', title='Standard Deviation for All Attribute Numbers in All of Lot Numbers')
                    fig.update_layout(xaxis_tickangle=-90)
                    fig.update_xaxes(type='category', dtick=1)
                    fig.update_traces(mode='lines+markers', line=dict(color='blue'), marker=dict(color='blue'))
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)

            # create checkbox to display plot
            plot = st.checkbox('Display Plot')

            # if checkbox is selected and attribute_number is not empty, iterate through all the selected Attribute_Number and display Plotly plot for each Attribute_Number
            if plot and 'All' in attribute_number:                  # NOTE - selection of Plot ###############################################################################################
                for i in df_filtered['Attribute_Number'].unique():
                    df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                    # create Plotly scatter plot
                    fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                    labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                    title='Plot for Attribute Number: ' + str(i))
                    # rotate Lot_Number labels by 90 degrees
                    fig.update_layout(xaxis_tickangle=-90)
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)
            
            elif plot and attribute_number:                         # NOTE - selection of Plot for selected Attribute_Number ###################################################################
                    for i in attribute_number:
                        df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                        # create Plotly scatter plot
                        fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                        labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                        title='Plot for Attribute Number: ' + str(i))
                        # rotate Lot_Number labels by 90 degrees
                        fig.update_layout(xaxis_tickangle=-90)
                        # display Plotly plot using Streamlit
                        st.plotly_chart(fig)
            # else:
            #     # display message to select Attribute_Number
            #     st.info('Please select Attribute Number to display plot')

        # check if Attribute_Number is selected
        elif attribute_number:                                      # NOTE - selection of Attribute_Number ###################################################################################
            # display subheader
            selected_attributes = ', '.join(attribute_number)
            st.markdown(f'<h3 style="font-size: 16px;">Attribute Number(s): {selected_attributes}</h3>', unsafe_allow_html=True)
            # filter dataframe based on Attribute_Number
            df_filtered = df_filtered[df_filtered['Attribute_Number'].isin(attribute_number)]

            # NOTE: display filtered dataframe
            # st.dataframe(df_filtered, width=2000)

            # create checkbox to display summary statistics
            summary = st.checkbox('Display Summary Statistics')

            # if checkbox is selected, display summary statistics for the filtered dataframe
            if summary:
                st.subheader('Summary Statistics')
                st.markdown('**Summary Statistics for All Lot Numbers**')
                # create a dataframe to display summary statistics for attribute_number
                df_summary = df_filtered.groupby(['Attribute_Number']).agg({'Attribute_Value': ['count', 'mean', 'std', 'min', 'max']})
                # rename columns
                df_summary.columns = ['Count', 'Mean', 'Standard Deviation', 'Minimum', 'Maximum']
                # sort df_summary by Attribute_Number
                df_summary = df_summary.sort_index()
                # display summary statistics dataframe
                st.dataframe(df_summary, width=2000)

                # create checkbox to plot the std of each attribute number
                plot_std = st.checkbox('Plot Standard Deviation')

                # if checkbox is selected, display scatter plot for the std of each attribute number
                if plot_std:
                    # create Plotly scatter plot
                    fig = px.scatter(df_summary, x=df_summary.index, y='Standard Deviation', title=f'Standard Deviation for Attribute Number(s): {selected_attributes}')
                    fig.update_layout(xaxis_tickangle=-90)
                    fig.update_xaxes(type='category', dtick=1)
                    fig.update_traces(mode='lines+markers', line=dict(color='blue'), marker=dict(color='blue'))
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)

            # create checkbox to display plot
            plot = st.checkbox('Display Plot')

            # if checkbox is selected and attribute_number is not empty, iterate through all the selected Attribute_Number and display Plotly plot for each Attribute_Number
            if plot and 'All' in attribute_number:                      # NOTE - selection of Plot ###############################################################################################
                for i in df_filtered['Attribute_Number'].unique():
                    df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                    # create Plotly scatter plot
                    fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                    labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                    title='Plot for Attribute Number: ' + str(i))
                    # rotate Lot_Number labels by 90 degrees
                    fig.update_layout(xaxis_tickangle=-90)
                    # display Plotly plot using Streamlit
                    st.plotly_chart(fig)
            
            elif plot and attribute_number:                               # NOTE - selection of Plot for selected Attribute_Number ###################################################################
                    for i in attribute_number:
                        df_plot = df_filtered[df_filtered['Attribute_Number'] == i]
                        # create Plotly scatter plot
                        fig = px.scatter(df_plot, x='Lot_Number', y='Attribute_Value', color='Serial_Number',
                                        labels={'Attribute_Value': 'Attribute Value', 'Lot_Number': 'Lot Number'},
                                        title='Plot for Attribute Number: ' + str(i))
                        # rotate Lot_Number labels by 90 degrees
                        fig.update_layout(xaxis_tickangle=-90)
                        # display Plotly plot using Streamlit
                        st.plotly_chart(fig)
            # else:
            #     # display message to select Attribute_Number
            #     st.info('Please select Attribute Number to display plot')
        else:
            # display message to select Attribute_Number
            st.info('Please select Attribute Number')
    else:
        # display message to select Lot_Number
        st.info('Please select Lot Number')
else:
    # display message to select a Part_Number
    st.info('Please select a Part Number')