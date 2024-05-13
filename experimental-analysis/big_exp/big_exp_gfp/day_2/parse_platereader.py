import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D7': ['B2', 'GFP10', 'RBS0.125', 16.484034820387237, 177.51596517961275], 'E9': ['B2', 'GFP10', 'RBS0.125', 16.484034820387237, 177.51596517961275], 'D6': ['C2', 'GFP25', 'RBS0.125', 15.157534678396281, 178.84246532160373], 'B6': ['C2', 'GFP25', 'RBS0.125', 15.157534678396281, 178.84246532160373], 'E5': ['D2', 'GFP50', 'RBS0.125', 17.42729169118082, 176.5727083088192], 'B10': ['D2', 'GFP50', 'RBS0.125', 17.42729169118082, 176.5727083088192], 'D11': ['E2', 'GFP75', 'RBS0.125', 16.647865131322867, 177.35213486867713], 'B5': ['E2', 'GFP75', 'RBS0.125', 16.647865131322867, 177.35213486867713], 'B11': ['B3', 'GFP10', 'RBS0.25', 14.888088515698387, 179.1119114843016], 'F3': ['B3', 'GFP10', 'RBS0.25', 14.888088515698387, 179.1119114843016], 'C3': ['C3', 'GFP25', 'RBS0.25', 15.162434228225004, 178.837565771775], 'B7': ['C3', 'GFP25', 'RBS0.25', 15.162434228225004, 178.837565771775], 'C6': ['D3', 'GFP50', 'RBS0.25', 14.780178584485679, 179.21982141551433], 'C8': ['D3', 'GFP50', 'RBS0.25', 14.780178584485679, 179.21982141551433], 'C5': ['E3', 'GFP75', 'RBS0.25', 16.177011208889542, 177.82298879111045], 'G2': ['E3', 'GFP75', 'RBS0.25', 16.177011208889542, 177.82298879111045], 'B8': ['B4', 'GFP10', 'RBS0.5', 14.368139322107062, 179.63186067789294], 'E4': ['B4', 'GFP10', 'RBS0.5', 14.368139322107062, 179.63186067789294], 'F8': ['C4', 'GFP25', 'RBS0.5', 14.177042519250039, 179.82295748074995], 'D8': ['C4', 'GFP25', 'RBS0.5', 14.177042519250039, 179.82295748074995], 'E11': ['D4', 'GFP50', 'RBS0.5', 14.04122495885724, 179.95877504114276], 'G8': ['D4', 'GFP50', 'RBS0.5', 14.04122495885724, 179.95877504114276], 'B9': ['E4', 'GFP75', 'RBS0.5', 12.91243699667013, 181.08756300332988], 'D5': ['E4', 'GFP75', 'RBS0.5', 12.91243699667013, 181.08756300332988], 'F6': ['B5', 'GFP10', 'RBS1', 17.260539687949443, 176.73946031205057], 'D4': ['B5', 'GFP10', 'RBS1', 17.260539687949443, 176.73946031205057], 'C4': ['C5', 'GFP25', 'RBS1', 13.621200957373574, 180.37879904262644], 'C7': ['C5', 'GFP25', 'RBS1', 13.621200957373574, 180.37879904262644], 'E8': ['D5', 'GFP50', 'RBS1', 15.559824038689973, 178.44017596131002], 'C9': ['D5', 'GFP50', 'RBS1', 15.559824038689973, 178.44017596131002], 'E3': ['E5', 'GFP75', 'RBS1', 15.361074565601413, 178.63892543439857], 'E2': ['E5', 'GFP75', 'RBS1', 15.361074565601413, 178.63892543439857], 'F7': ['B6', 'GFP10', 'RBS2', 15.167336946557155, 178.83266305344284], 'D2': ['B6', 'GFP10', 'RBS2', 15.167336946557155, 178.83266305344284], 'G11': ['C6', 'GFP25', 'RBS2', 14.385767887360423, 179.61423211263957], 'B4': ['C6', 'GFP25', 'RBS2', 14.385767887360423, 179.61423211263957], 'F5': ['D6', 'GFP50', 'RBS2', 14.211407804175272, 179.78859219582472], 'G9': ['D6', 'GFP50', 'RBS2', 14.211407804175272, 179.78859219582472], 'D9': ['E6', 'GFP75', 'RBS2', 14.198501476331673, 179.80149852366833], 'G3': ['E6', 'GFP75', 'RBS2', 14.198501476331673, 179.80149852366833], 'F11': ['B7', 'GFP10', 'RBS4', 13.781297676024332, 180.21870232397566], 'E6': ['B7', 'GFP10', 'RBS4', 13.781297676024332, 180.21870232397566], 'D3': ['C7', 'GFP25', 'RBS4', 13.023589111341503, 180.9764108886585], 'C2': ['C7', 'GFP25', 'RBS4', 13.023589111341503, 180.9764108886585], 'B2': ['D7', 'GFP50', 'RBS4', 14.164197231724573, 179.8358027682754], 'C11': ['D7', 'GFP50', 'RBS4', 14.164197231724573, 179.8358027682754], 'B3': ['E7', 'GFP75', 'RBS4', 14.733746703467382, 179.26625329653262], 'E10': ['E7', 'GFP75', 'RBS4', 14.733746703467382, 179.26625329653262], 'C10': ['blank', 'blank', 'blank', 0, 194], 'D10': ['blank', 'blank', 'blank', 0, 194], 'E7': ['blank', 'blank', 'blank', 0, 194], 'F2': ['blank', 'blank', 'blank', 0, 194], 'F4': ['blank', 'blank', 'blank', 0, 194], 'F9': ['blank', 'blank', 'blank', 0, 194], 'F10': ['blank', 'blank', 'blank', 0, 194], 'G4': ['blank', 'blank', 'blank', 0, 194], 'G5': ['blank', 'blank', 'blank', 0, 194], 'G6': ['blank', 'blank', 'blank', 0, 194], 'G7': ['blank', 'blank', 'blank', 0, 194], 'G10': ['blank', 'blank', 'blank', 0, 194]}

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
    file = "122123_post.xlsx"

    categories = ['GFP_high', 'GFP_low', 'OD600']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('day_2_gfp_clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
