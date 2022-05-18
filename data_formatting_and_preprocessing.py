import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

question_id_original = 19
question_id_counterpart = 34

dtype_original_grade_pred = {'Q19_1_TEXT': float, 'Q19_2_TEXT': float, 'Q19_3_TEXT': float, 'Q19_4_TEXT': float, 'Q19_5_TEXT': float,
           'Q19_6_TEXT': float, 'Q19_7_TEXT': float, 'Q19_8_TEXT': float}
dtype_original_grade_ranking = {'Q19_1': int, 'Q19_2': int, 'Q19_3': int, 'Q19_4': int, 'Q19_5': int,
           'Q19_6': int, 'Q19_7': int, 'Q19_8': int}
dtype_counterpart_grade_pred = {'Q34_1_TEXT':float, 'Q34_2_TEXT':float, 'Q34_3_TEXT':float, 'Q34_4_TEXT':float, 'Q34_5_TEXT':float, 'Q34_6_TEXT':float, 'Q34_7_TEXT':float, 'Q34_8_TEXT':float}
dtype_counterpart_grade_ranking = {'Q34_1':int, 'Q34_2':int, 'Q34_3':int, 'Q34_4':int, 'Q34_5':int, 'Q34_6':int, 'Q34_7':int, 'Q34_8':int}

name_to_question_id_dict ={'Anna': 1, 'Jenny': 2, 'Brian':3, 'Oliver':4, 'Sarah': 5, 'Michael':6, 'Lisa': 7, 'David': 8}


question_id_to_name = {1: 'Anna', 2:'Jenny', 3: 'Brian', 4:'Oliver',  5:'Sarah', 6: 'Michael', 7: 'Lisa', 8: 'David'}
female_vignettes = {'982': 8, '881': 10, '817': 13, '348': 15}
male_ids_and_grades = {'927': 8, '868': 10, '590':13, '806':15}
all_vignettes = ['982', '881', '817', '348', '927', '868', '590', '806']

stereotype_activation_types = "None", "CaseBased", "Statistics"


def load_file():
    counter = pd.read_excel('Counterpart.xlsx', header=1, dtype=dtype_counterpart_grade_pred, skiprows = [2, 3])
    original = pd.read_excel('Original.xlsx', header=1, dtype=dtype_original_grade_pred, skiprows = [2, 3])
    return counter, original


def filter_out_wrong_grade_range(data, columns, question_id):
    column_name = "Q" + str(question_id) + "_1_TEXT"
    predicted_grades = data[columns]
    max_per_row = predicted_grades.max(axis=1)
    max_is_bigger_than_20_rows = max_per_row[max_per_row>20].index.values
    max_is_smaller_than_10_rows = max_per_row[max_per_row<=10].index.values
    rows_with_NaN = data[column_name].index[data[column_name].apply(np.isnan)].values

    data = data.drop(max_is_bigger_than_20_rows, axis=0)
    data = data.drop(max_is_smaller_than_10_rows, axis=0)
    data = data.drop(rows_with_NaN, axis=0).reset_index(drop=True)

    return data

def filter_out_wrong_grade_orders(data, columns_prediction, columns_ranking):
    predicted_grades = data[columns_prediction]
    predicted_grade_rankings = data[columns_ranking]

    wrong_orderings = []
    for index, row in predicted_grades.iterrows():
        ordered_row_according_to_grades = ((row*-1).argsort().argsort()+1).array
        ordered_row_according_to_participant = predicted_grade_rankings.loc[index].array
        difference_in_ordering = abs(ordered_row_according_to_grades-ordered_row_according_to_participant)
        if max(difference_in_ordering) >=3:
            wrong_orderings.append(index)
    print(wrong_orderings)
    data = data.drop(wrong_orderings, axis=0).reset_index(drop=True)
    return data



def filter_out_short_responses(data):
    duration = data['Duration (in seconds)']
    too_little_time_indices = set(duration.index[duration <= 150])
    data = data.drop(too_little_time_indices, axis=0).reset_index(drop=True)

    return data



def extract_vignette_grades(data, question_id):
    column_name = "Q"+str(question_id) +"_"
    predicted_rankings_per_vignette = {'982_rank': [], '881_rank': [], '817_rank': [], '348_rank': [], '927_rank': [], '868_rank': [], '590_rank': [],
                                       '806_rank': []}
    predicted_grades_per_vignette = {'982_grade': [], '881_grade': [], '817_grade': [], '348_grade': [], '927_grade': [], '868_grade': [], '590_grade': [],
                                     '806_grade': []}

    for index, row in data.iterrows():
        for i in range(1, 9):
            grade_for_student_i = int(row[column_name+str(i)+'_TEXT'])
            ranking_for_student_i = int(row[column_name+str(i)])
            name_corresponding_to_i = question_id_to_name[i]
            vignette_number_corresponding_to_name = str(int(row[name_corresponding_to_i]))
            predicted_rankings_per_vignette[str(vignette_number_corresponding_to_name)+'_rank'].append(ranking_for_student_i)
            predicted_grades_per_vignette[str(vignette_number_corresponding_to_name)+'_grade'].append(grade_for_student_i)

    return predicted_grades_per_vignette, predicted_rankings_per_vignette

def merge_with_rest_of_data(org_data, org_predicted_grades, org_predicted_rankings, counter_data, counter_predicted_grades, counter_predicted_rankings):
    df_org_grades = pd.DataFrame.from_dict(org_predicted_grades)
    df_org_rankings = pd.DataFrame.from_dict(org_predicted_rankings)
    df_org = pd.concat([df_org_grades, df_org_rankings], axis=1)
    df_org['Stereotype Activation'] = org_data['Stereotype Activation']
    df_org['Datatype'] = org_data['Datatype']
    df_org['Duration (in seconds)'] = org_data['Duration (in seconds)']
    df_org['Gender'] = org_data['Q27']
    df_org['Age'] = org_data['Q28']
    df_org['Nationality'] = org_data['Q29']
    df_org['English Proficiency'] = org_data['Q30']
    df_org['Background'] = org_data['Q31']

    df_counter_grades = pd.DataFrame.from_dict(counter_predicted_grades)
    df_counter_rankings = pd.DataFrame.from_dict(counter_predicted_rankings)
    df_counter = pd.concat([df_counter_grades, df_counter_rankings], axis=1)
    df_counter['Stereotype Activation'] = counter_data['Stereotype Activation']
    df_counter['Datatype'] = counter_data['Datatype']
    df_counter['Duration (in seconds)'] = counter_data['Duration (in seconds)']
    df_counter['Gender'] = counter_data['Q27']
    df_counter['Age'] = counter_data['Q28']
    df_counter['Nationality'] = counter_data['Q29']
    df_counter['English Proficiency'] = counter_data['Q30']
    df_counter['Background'] = counter_data['Q31']

    merged = pd.concat([df_org, df_counter], ignore_index=True)
    print(merged.shape)

    return merged


def remove_outliers(merged_data):
    all_outliers = []
    for datatype in ['Org', 'Counterpart']:
        for stereotype_activation in stereotype_activation_types:
            for vignette_number in all_vignettes:
                applicable_data = merged_data[(merged_data["Datatype"] == datatype) & (merged_data['Stereotype Activation'] == stereotype_activation)]

                predictions = applicable_data[str(vignette_number)+'_grade']
                first_quantile = predictions.quantile(.25)
                third_quantile = predictions.quantile(.75)
                inter_quantile_range = third_quantile-first_quantile

                lower_outliers = predictions.index[predictions < (first_quantile - 1.5 * inter_quantile_range)].values
                upper_outliers = predictions.index[predictions > (third_quantile + 1.5 * inter_quantile_range)].values
                all_outliers.extend(lower_outliers)
                all_outliers.extend(upper_outliers)
                #all_outliers = [y for x in [lower_outliers, upper_outliers] for y in x]
                #merged_data.loc[all_outliers, vignette_number] = ' '

    # set_all_outliers = set(all_outliers)
    # merged_data = merged_data.drop(set_all_outliers, axis=0)
    import collections
    duplicates = [item for item, count in collections.Counter(all_outliers).items() if count > 1]
    outlier_data = merged_data.loc[duplicates]

    merged_data = merged_data.drop([125, 160, 122, 166], axis=0)
    # merged_data = merged_data.drop(upper_outliers, axis=0).reset_index(drop=True)
    print(merged_data.shape)
    return merged_data


def complete_formatting_and_preprocessing():
    counter, original = load_file()
    original = filter_out_wrong_grade_range(original, dtype_original_grade_pred.keys(), question_id_original)
    original = filter_out_wrong_grade_orders(original, dtype_original_grade_pred.keys(),
                                             dtype_original_grade_ranking.keys())
    predicted_grades_org, predicted_rankings_org = extract_vignette_grades(original, question_id_original)
    #
    counter = filter_out_wrong_grade_range(counter, dtype_counterpart_grade_pred.keys(), question_id_counterpart)
    counter = filter_out_wrong_grade_orders(counter, dtype_counterpart_grade_pred.keys(),
                                            dtype_counterpart_grade_ranking.keys())

    predicted_grades_counter, predicted_rankings_counter = extract_vignette_grades(counter, question_id_counterpart)

    merged = merge_with_rest_of_data(original, predicted_grades_org, predicted_rankings_org, counter,
                                     predicted_grades_counter, predicted_rankings_counter)
    merged = filter_out_short_responses(merged)
    merged.drop([125], axis=0)
    merged.to_excel('FinalData.xlsx')
    #outlier_removed = remove_outliers(merged)
    # print(outlier_removed.shape)
    #
    # outlier_removed.to_excel('04_04_Without_Outliers.xlsx')