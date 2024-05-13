import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D7': ['B2', 'GFP10', 'RBS0.125', 21.21506184461401, 172.784938155386], 'B9': ['B2', 'GFP10', 'RBS0.125', 21.21506184461401, 172.784938155386], 'C9': ['C2', 'GFP25', 'RBS0.125', 22.084143988874462, 171.91585601112553], 'E3': ['C2', 'GFP25', 'RBS0.125', 22.084143988874462, 171.91585601112553], 'D6': ['D2', 'GFP50', 'RBS0.125', 26.456746023621342, 167.54325397637865], 'C2': ['D2', 'GFP50', 'RBS0.125', 26.456746023621342, 167.54325397637865], 'F6': ['E2', 'GFP75', 'RBS0.125', 21.76642259804219, 172.2335774019578], 'B4': ['E2', 'GFP75', 'RBS0.125', 21.76642259804219, 172.2335774019578], 'G7': ['B3', 'GFP10', 'RBS0.25', 27.463737638503975, 166.53626236149603], 'F11': ['B3', 'GFP10', 'RBS0.25', 27.463737638503975, 166.53626236149603], 'B7': ['C3', 'GFP25', 'RBS0.25', 21.006025166574744, 172.99397483342526], 'E7': ['C3', 'GFP25', 'RBS0.25', 21.006025166574744, 172.99397483342526], 'E6': ['D3', 'GFP50', 'RBS0.25', 28.831227119286407, 165.1687728807136], 'G11': ['D3', 'GFP50', 'RBS0.25', 28.831227119286407, 165.1687728807136], 'D9': ['E3', 'GFP75', 'RBS0.25', 23.43009884017745, 170.56990115982256], 'E10': ['E3', 'GFP75', 'RBS0.25', 23.43009884017745, 170.56990115982256], 'E2': ['B4', 'GFP10', 'RBS0.5', 24.166533613764667, 169.83346638623533], 'C11': ['B4', 'GFP10', 'RBS0.5', 24.166533613764667, 169.83346638623533], 'F2': ['C4', 'GFP25', 'RBS0.5', 22.357858333965762, 171.64214166603423], 'C3': ['C4', 'GFP25', 'RBS0.5', 22.357858333965762, 171.64214166603423], 'F5': ['D4', 'GFP50', 'RBS0.5', 28.207005483378904, 165.7929945166211], 'G5': ['D4', 'GFP50', 'RBS0.5', 28.207005483378904, 165.7929945166211], 'D2': ['E4', 'GFP75', 'RBS0.5', 19.658891921868708, 174.3411080781313], 'G10': ['E4', 'GFP75', 'RBS0.5', 19.658891921868708, 174.3411080781313], 'D10': ['B5', 'GFP10', 'RBS1', 27.383564280190214, 166.61643571980977], 'B3': ['B5', 'GFP10', 'RBS1', 27.383564280190214, 166.61643571980977], 'F3': ['C5', 'GFP25', 'RBS1', 20.90304262953785, 173.09695737046215], 'B10': ['C5', 'GFP25', 'RBS1', 20.90304262953785, 173.09695737046215], 'E8': ['D5', 'GFP50', 'RBS1', 26.2054480905526, 167.7945519094474], 'D4': ['D5', 'GFP50', 'RBS1', 26.2054480905526, 167.7945519094474], 'G3': ['E5', 'GFP75', 'RBS1', 20.72752107223029, 173.27247892776973], 'G9': ['E5', 'GFP75', 'RBS1', 20.72752107223029, 173.27247892776973], 'B8': ['B6', 'GFP10', 'RBS2', 30.147005267337402, 163.8529947326626], 'F4': ['B6', 'GFP10', 'RBS2', 30.147005267337402, 163.8529947326626], 'B6': ['C6', 'GFP25', 'RBS2', 20.987225406747935, 173.01277459325206], 'F7': ['C6', 'GFP25', 'RBS2', 20.987225406747935, 173.01277459325206], 'E11': ['D6', 'GFP50', 'RBS2', 26.016474201323664, 167.98352579867634], 'C4': ['D6', 'GFP50', 'RBS2', 26.016474201323664, 167.98352579867634], 'D11': ['E6', 'GFP75', 'RBS2', 22.78139751066313, 171.21860248933686], 'C6': ['E6', 'GFP75', 'RBS2', 22.78139751066313, 171.21860248933686], 'C10': ['B7', 'GFP10', 'RBS4', 25.68873085739381, 168.3112691426062], 'G4': ['B7', 'GFP10', 'RBS4', 25.68873085739381, 168.3112691426062], 'D8': ['C7', 'GFP25', 'RBS4', 20.314542797671965, 173.68545720232802], 'C5': ['C7', 'GFP25', 'RBS4', 20.314542797671965, 173.68545720232802], 'E5': ['D7', 'GFP50', 'RBS4', 24.21644597953246, 169.78355402046753], 'D5': ['D7', 'GFP50', 'RBS4', 24.21644597953246, 169.78355402046753], 'C8': ['E7', 'GFP75', 'RBS4', 20.4029137837116, 173.5970862162884], 'G6': ['E7', 'GFP75', 'RBS4', 20.4029137837116, 173.5970862162884], 'B2': ['blank', 'blank', 'blank', 0, 194], 'B5': ['blank', 'blank', 'blank', 0, 194], 'B11': ['blank', 'blank', 'blank', 0, 194], 'C7': ['blank', 'blank', 'blank', 0, 194], 'D3': ['blank', 'blank', 'blank', 0, 194], 'E4': ['blank', 'blank', 'blank', 0, 194], 'E9': ['blank', 'blank', 'blank', 0, 194], 'F8': ['blank', 'blank', 'blank', 0, 194], 'F9': ['blank', 'blank', 'blank', 0, 194], 'F10': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194], 'G8': ['blank', 'blank', 'blank', 0, 194]}

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
    merged_dataframe = merged_dataframe[['time', 'well', 'iptg', 'strain', 'rbs', 'temp', 'OD600', 'fluor', 'GFP_high', 'GFP_low']]


    # Find the average of the blanks at each timepoint
    blank_df = merged_dataframe[merged_dataframe['rbs'] == 'blank']
    blank_df = blank_df[['time', 'OD600', 'GFP_high', 'GFP_low']]
    blank_df = blank_df.groupby(by='time').mean()
    blank_df = blank_df.reset_index()
    print(blank_df.head())

    # Subtract the blank from the other data
    merged_dataframe = merged_dataframe[merged_dataframe['rbs'] != 'blank']
    merged_dataframe = pd.merge(merged_dataframe, blank_df, on='time', suffixes=('', '_blank'))
    merged_dataframe['OD600'] = merged_dataframe['OD600'] - merged_dataframe['OD600_blank']
    merged_dataframe['GFP_high'] = merged_dataframe['GFP_high'] - merged_dataframe['GFP_high_blank']
    merged_dataframe['GFP_low'] = merged_dataframe['GFP_low'] - merged_dataframe['GFP_low_blank']
    merged_dataframe = merged_dataframe.drop(columns=['OD600_blank', 'GFP_high_blank', 'GFP_low_blank'])

    # Drop the blank from the table
    merged_dataframe = merged_dataframe[merged_dataframe.rbs != 'blank']


    #print(merged_dataframe.head())
    return merged_dataframe, start_time


def main():
    file = "122023_post.xlsx"

    categories = ['GFP_high', 'GFP_low', 'OD600']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('day_1_gfp_clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
