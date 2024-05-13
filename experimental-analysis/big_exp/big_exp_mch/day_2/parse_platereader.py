import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'B9': ['B2', 'MCH10', 'RBS0.125', 19.079101845534915, 174.92089815446508], 'G8': ['B2', 'MCH10', 'RBS0.125', 19.079101845534915, 174.92089815446508], 'D10': ['C2', 'MCH25', 'RBS0.125', 15.929761022993219, 178.0702389770068], 'B6': ['C2', 'MCH25', 'RBS0.125', 15.929761022993219, 178.0702389770068], 'D5': ['D2', 'MCH50', 'RBS0.125', 17.279616515662262, 176.72038348433773], 'G10': ['D2', 'MCH50', 'RBS0.125', 17.279616515662262, 176.72038348433773], 'B8': ['E2', 'MCH75', 'RBS0.125', 14.925993257698082, 179.07400674230192], 'D6': ['E2', 'MCH75', 'RBS0.125', 14.925993257698082, 179.07400674230192], 'G3': ['B3', 'MCH10', 'RBS0.25', 30.351853796258947, 163.64814620374105], 'C11': ['B3', 'MCH10', 'RBS0.25', 30.351853796258947, 163.64814620374105], 'F7': ['C3', 'MCH25', 'RBS0.25', 15.94058949133155, 178.05941050866846], 'C7': ['C3', 'MCH25', 'RBS0.25', 15.94058949133155, 178.05941050866846], 'B7': ['D3', 'MCH50', 'RBS0.25', 18.085877218289113, 175.9141227817109], 'C10': ['D3', 'MCH50', 'RBS0.25', 18.085877218289113, 175.9141227817109], 'G7': ['E3', 'MCH75', 'RBS0.25', 17.078270392777906, 176.9217296072221], 'C5': ['E3', 'MCH75', 'RBS0.25', 17.078270392777906, 176.9217296072221], 'D3': ['B4', 'MCH10', 'RBS0.5', 19.25138956410062, 174.74861043589937], 'F2': ['B4', 'MCH10', 'RBS0.5', 19.25138956410062, 174.74861043589937], 'B3': ['C4', 'MCH25', 'RBS0.5', 17.716951825156112, 176.28304817484388], 'G9': ['C4', 'MCH25', 'RBS0.5', 17.716951825156112, 176.28304817484388], 'C4': ['D4', 'MCH50', 'RBS0.5', 21.11477865862336, 172.88522134137665], 'D4': ['D4', 'MCH50', 'RBS0.5', 21.11477865862336, 172.88522134137665], 'F8': ['E4', 'MCH75', 'RBS0.5', 17.203558281130455, 176.79644171886954], 'E11': ['E4', 'MCH75', 'RBS0.5', 17.203558281130455, 176.79644171886954], 'E6': ['B5', 'MCH10', 'RBS1', 17.38852591897787, 176.61147408102212], 'B4': ['B5', 'MCH10', 'RBS1', 17.38852591897787, 176.61147408102212], 'G2': ['C5', 'MCH25', 'RBS1', 17.44025237658028, 176.55974762341972], 'D7': ['C5', 'MCH25', 'RBS1', 17.44025237658028, 176.55974762341972], 'G6': ['D5', 'MCH50', 'RBS1', 17.33710347753549, 176.6628965224645], 'E3': ['D5', 'MCH50', 'RBS1', 17.33710347753549, 176.6628965224645], 'C6': ['E5', 'MCH75', 'RBS1', 14.93074423959493, 179.06925576040507], 'F3': ['E5', 'MCH75', 'RBS1', 14.93074423959493, 179.06925576040507], 'F6': ['B6', 'MCH10', 'RBS2', 16.93031251079206, 177.06968748920795], 'E2': ['B6', 'MCH10', 'RBS2', 16.93031251079206, 177.06968748920795], 'D8': ['C6', 'MCH25', 'RBS2', 16.71312179333458, 177.28687820666542], 'E9': ['C6', 'MCH25', 'RBS2', 16.71312179333458, 177.28687820666542], 'D2': ['D6', 'MCH50', 'RBS2', 17.73705170754554, 176.26294829245447], 'G5': ['D6', 'MCH50', 'RBS2', 17.73705170754554, 176.26294829245447], 'E8': ['E6', 'MCH75', 'RBS2', 16.63605633327214, 177.36394366672786], 'E4': ['E6', 'MCH75', 'RBS2', 16.63605633327214, 177.36394366672786], 'D9': ['B7', 'MCH10', 'RBS4', 18.01640182170399, 175.983598178296], 'C3': ['B7', 'MCH10', 'RBS4', 18.01640182170399, 175.983598178296], 'B10': ['C7', 'MCH25', 'RBS4', 15.80628521779984, 178.19371478220017], 'F4': ['C7', 'MCH25', 'RBS4', 15.80628521779984, 178.19371478220017], 'D11': ['D7', 'MCH50', 'RBS4', 17.485766862414867, 176.51423313758514], 'G11': ['D7', 'MCH50', 'RBS4', 17.485766862414867, 176.51423313758514], 'C2': ['E7', 'MCH75', 'RBS4', 30.293040875998685, 163.70695912400132], 'C9': ['E7', 'MCH75', 'RBS4', 30.293040875998685, 163.70695912400132], 'B2': ['blank', 'blank', 'blank', 0, 194], 'B5': ['blank', 'blank', 'blank', 0, 194], 'B11': ['blank', 'blank', 'blank', 0, 194], 'C8': ['blank', 'blank', 'blank', 0, 194], 'E5': ['blank', 'blank', 'blank', 0, 194], 'E7': ['blank', 'blank', 'blank', 0, 194], 'E10': ['blank', 'blank', 'blank', 0, 194], 'F5': ['blank', 'blank', 'blank', 0, 194], 'F9': ['blank', 'blank', 'blank', 0, 194], 'F10': ['blank', 'blank', 'blank', 0, 194], 'F11': ['blank', 'blank', 'blank', 0, 194], 'G4': ['blank', 'blank', 'blank', 0, 194]}

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
    file = "122823_post.xlsx"

    categories = ['mCherry_high', 'mCherry_low', 'OD600']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('day_2_mch_clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
