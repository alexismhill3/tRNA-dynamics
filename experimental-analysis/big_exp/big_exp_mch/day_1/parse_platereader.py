import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D7': ['B2', 'MCH10', 'RBS0.125', 27.11051958204659, 166.88948041795342], 'B9': ['B2', 'MCH10', 'RBS0.125', 27.11051958204659, 166.88948041795342], 'C9': ['C2', 'MCH25', 'RBS0.125', 27.54034006747656, 166.45965993252344], 'E3': ['C2', 'MCH25', 'RBS0.125', 27.54034006747656, 166.45965993252344], 'D6': ['D2', 'MCH50', 'RBS0.125', 29.18556504149148, 164.8144349585085], 'C2': ['D2', 'MCH50', 'RBS0.125', 29.18556504149148, 164.8144349585085], 'F6': ['E2', 'MCH75', 'RBS0.125', 23.978118697819077, 170.02188130218093], 'B4': ['E2', 'MCH75', 'RBS0.125', 23.978118697819077, 170.02188130218093], 'G7': ['B3', 'MCH10', 'RBS0.25', 47.95623830898639, 146.0437616910136], 'F11': ['B3', 'MCH10', 'RBS0.25', 47.95623830898639, 146.0437616910136], 'B7': ['C3', 'MCH25', 'RBS0.25', 25.587127055979188, 168.41287294402082], 'E7': ['C3', 'MCH25', 'RBS0.25', 25.587127055979188, 168.41287294402082], 'E6': ['D3', 'MCH50', 'RBS0.25', 27.524180029883194, 166.47581997011682], 'G11': ['D3', 'MCH50', 'RBS0.25', 27.524180029883194, 166.47581997011682], 'D9': ['E3', 'MCH75', 'RBS0.25', 27.252294574103352, 166.74770542589664], 'E10': ['E3', 'MCH75', 'RBS0.25', 27.252294574103352, 166.74770542589664], 'E2': ['B4', 'MCH10', 'RBS0.5', 29.70310288118569, 164.29689711881431], 'C11': ['B4', 'MCH10', 'RBS0.5', 29.70310288118569, 164.29689711881431], 'F2': ['C4', 'MCH25', 'RBS0.5', 29.816403353867976, 164.18359664613203], 'C3': ['C4', 'MCH25', 'RBS0.5', 29.816403353867976, 164.18359664613203], 'F5': ['D4', 'MCH50', 'RBS0.5', 31.9490478950477, 162.0509521049523], 'G5': ['D4', 'MCH50', 'RBS0.5', 31.9490478950477, 162.0509521049523], 'D2': ['E4', 'MCH75', 'RBS0.5', 26.056221726102113, 167.9437782738979], 'G10': ['E4', 'MCH75', 'RBS0.5', 26.056221726102113, 167.9437782738979], 'D10': ['B5', 'MCH10', 'RBS1', 50.70400138857561, 143.29599861142438], 'B3': ['B5', 'MCH10', 'RBS1', 50.70400138857561, 143.29599861142438], 'F3': ['C5', 'MCH25', 'RBS1', 27.411574281776502, 166.5884257182235], 'B10': ['C5', 'MCH25', 'RBS1', 27.411574281776502, 166.5884257182235], 'E8': ['D5', 'MCH50', 'RBS1', 27.141898029248633, 166.85810197075136], 'D4': ['D5', 'MCH50', 'RBS1', 27.141898029248633, 166.85810197075136], 'G3': ['E5', 'MCH75', 'RBS1', 21.633394782203748, 172.36660521779626], 'G9': ['E5', 'MCH75', 'RBS1', 21.633394782203748, 172.36660521779626], 'B8': ['B6', 'MCH10', 'RBS2', 30.85605437999492, 163.14394562000507], 'F4': ['B6', 'MCH10', 'RBS2', 30.85605437999492, 163.14394562000507], 'B6': ['C6', 'MCH25', 'RBS2', 26.408334433225058, 167.59166556677494], 'F7': ['C6', 'MCH25', 'RBS2', 26.408334433225058, 167.59166556677494], 'E11': ['D6', 'MCH50', 'RBS2', 25.685215292817986, 168.314784707182], 'C4': ['D6', 'MCH50', 'RBS2', 25.685215292817986, 168.314784707182], 'D11': ['E6', 'MCH75', 'RBS2', 22.767573200910675, 171.23242679908932], 'C6': ['E6', 'MCH75', 'RBS2', 22.767573200910675, 171.23242679908932], 'C10': ['B7', 'MCH10', 'RBS4', 41.359085216306774, 152.64091478369323], 'G4': ['B7', 'MCH10', 'RBS4', 41.359085216306774, 152.64091478369323], 'D8': ['C7', 'MCH25', 'RBS4', 26.800684459150148, 167.19931554084985], 'C5': ['C7', 'MCH25', 'RBS4', 26.800684459150148, 167.19931554084985], 'E5': ['D7', 'MCH50', 'RBS4', 28.933500778248373, 165.06649922175163], 'D5': ['D7', 'MCH50', 'RBS4', 28.933500778248373, 165.06649922175163], 'C8': ['E7', 'MCH75', 'RBS4', 35.82979596918771, 158.1702040308123], 'G6': ['E7', 'MCH75', 'RBS4', 35.82979596918771, 158.1702040308123], 'B2': ['blank', 'blank', 'blank', 0, 194], 'B5': ['blank', 'blank', 'blank', 0, 194], 'B11': ['blank', 'blank', 'blank', 0, 194], 'C7': ['blank', 'blank', 'blank', 0, 194], 'D3': ['blank', 'blank', 'blank', 0, 194], 'E4': ['blank', 'blank', 'blank', 0, 194], 'E9': ['blank', 'blank', 'blank', 0, 194], 'F8': ['blank', 'blank', 'blank', 0, 194], 'F9': ['blank', 'blank', 'blank', 0, 194], 'F10': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194], 'G8': ['blank', 'blank', 'blank', 0, 194]}

for well, data in well_encoding.items():
    if isinstance(data[2], float):
        data[2] = data[2]/4
    well_encoding[well] = [str(data[1]), str(data[2])]
    print(well_encoding[well])



def is_empty(row):
    if not any(row):
        return True
    else:
        return False

def parse_platereader(filename, categories):
    wb =  xl.load_workbook(filename)
    ws = wb.active
    in_data = False
    dataframes = []
    timepoints = []
    temperature = []
    start_time = None
    for row in ws.rows:
        row_values = [cell.value for cell in row]

        if row_values[0] == 'Start Time':
            start_time = row_values[1]
            continue

        if row_values[0] in categories:
            in_data = row_values[0]
            df = pd.DataFrame(columns=['time', 'well', 'iptg', 'rbs' 'temp',  'fluor', 'strain', in_data])
            continue

        if in_data and is_empty(row_values):
            in_data = False
            # Save the data
            dataframes.append(df)
            continue

        if in_data:
            if row_values[0] == 'Cycle Nr.':
                continue
            elif row_values[0] == 'Time [s]':
                timepoints = row_values[1:]
                # Round timepoints to nearest second
                timepoints = [round(timepoint) for timepoint in timepoints if timepoint is not None]
                continue
            elif row_values[0] == 'Temp. [°C]':
                temperature = row_values[1:]
                temperature = [temp for temp in temperature if temp is not None]
                continue
            else:
                well = row_values[0]
                values = row_values[1:]
                values = [value for value in values if value is not None]
                #print(len(timepoints), len(values), len(temperature))
                if 'blank' in well_encoding[well][0]:
                    fluor = 'blank'
                elif 'G' in well_encoding[well][0]:
                    fluor = 'GFP'
                elif 'M' in well_encoding[well][0]:
                    fluor = 'mCherry'
                else:
                    fluor = 'unknown'
                temp_dataframe = pd.DataFrame({'time': timepoints, 'well': well, 'iptg':'0.01875', 'rbs':well_encoding[well][1], 'temp': temperature, 'fluor':fluor, 'strain': well_encoding[well][0], in_data: values})
                df = pd.concat([df, temp_dataframe], ignore_index=True)
                continue

        continue

    merged_dataframe = pd.concat(dataframes, axis=1)
    merged_dataframe = merged_dataframe.replace('OVER', float('inf'))
    merged_dataframe = merged_dataframe.groupby(by=merged_dataframe.columns, axis=1).apply(lambda g: g.mean(axis=1) if isinstance(g.iloc[0,0], numbers.Number) else g.iloc[:,0]) # https://stackoverflow.com/questions/40311987/pandas-mean-of-columns-with-the-same-names
    
    # Fix order
    merged_dataframe = merged_dataframe[['time', 'well', 'iptg', 'strain', 'rbs', 'temp', 'OD600', 'fluor', 'mCherry_high', 'mCherry_low']]


    # Find the average of the blanks at each timepoint
    blank_df = merged_dataframe[merged_dataframe['rbs'] == 'blank']
    blank_df = blank_df[['time', 'OD600', 'mCherry_high', 'mCherry_low']]
    blank_df = blank_df.groupby(by='time').mean()
    blank_df = blank_df.reset_index()
    print(blank_df.head())

    # Subtract the blank from the other data
    merged_dataframe = merged_dataframe[merged_dataframe['rbs'] != 'blank']
    merged_dataframe = pd.merge(merged_dataframe, blank_df, on='time', suffixes=('', '_blank'))
    merged_dataframe['OD600'] = merged_dataframe['OD600'] - merged_dataframe['OD600_blank']
    merged_dataframe['mCherry_high'] = merged_dataframe['mCherry_high'] - merged_dataframe['mCherry_high_blank']
    merged_dataframe['mCherry_low'] = merged_dataframe['mCherry_low'] - merged_dataframe['mCherry_low_blank']
    merged_dataframe = merged_dataframe.drop(columns=['OD600_blank', 'mCherry_high_blank', 'mCherry_low_blank'])

    # Drop the blank from the table
    merged_dataframe = merged_dataframe[merged_dataframe.rbs != 'blank']


    #print(merged_dataframe.head())
    return merged_dataframe, start_time


def main():
    file = "122723_post.xlsx"

    categories = ['mCherry_high', 'mCherry_low', 'OD600']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('day_1_mch_clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
