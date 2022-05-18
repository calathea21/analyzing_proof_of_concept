import pandas as pd
import plotnine as p9
import patchworklib as pw
from data_formatting_and_preprocessing import complete_formatting_and_preprocessing
import scipy.stats
#p9.options.figure_size = (7, 6.1)
#p9.options.figure_size = (8.63, 6.1)


def load_final_data():
    data = pd.read_excel("FinalData.xlsx")
    data = data.drop(columns=["Unnamed: 0"])
    return data

def calculate_means_and_standard_errors(data, vignette_id, female):
    vignette_column = str(vignette_id) +"_grade"
    counterpart_data_pred, org_data_pred = [x for _, x in data.groupby(data['Datatype'] == "Org")]

    mean_org_across_stereotype_act = org_data_pred.groupby("Stereotype Activation")[vignette_column].mean()
    mean_counterpart_across_stereotype_act = counterpart_data_pred.groupby("Stereotype Activation")[vignette_column].mean()

    standard_error_org_across_stereotype_act = org_data_pred.groupby("Stereotype Activation")[vignette_column].std() / (org_data_pred.groupby("Stereotype Activation")[vignette_column].size()**(1/2))
    standard_error_counterpart_across_stereotype_act = counterpart_data_pred.groupby("Stereotype Activation")[vignette_column].std() / (counterpart_data_pred.groupby("Stereotype Activation")[vignette_column].size() ** (1 / 2))

    df_org_across_stereotype_act = org_data_pred.groupby("Stereotype Activation")[vignette_column].size() - 1
    df_counterpart_across_stereotype_act = counterpart_data_pred.groupby("Stereotype Activation")[vignette_column].size() - 1

    dataframe_org = pd.DataFrame(mean_org_across_stereotype_act)
    dataframe_org["Sex"] = "Female" if female else "Male"
    dataframe_org["Standard_error"] = standard_error_org_across_stereotype_act.tolist()
    dataframe_org["Degrees_of_freedom"] = df_org_across_stereotype_act.tolist()
    dataframe_org["Confidence_interval"] = scipy.stats.t.ppf(q=1-.05/2, df=dataframe_org["Degrees_of_freedom"]) * dataframe_org["Standard_error"]

    dataframe_counter = pd.DataFrame(mean_counterpart_across_stereotype_act)
    dataframe_counter["Sex"] = "Male" if female else "Female"
    dataframe_counter["Standard_error"] = standard_error_counterpart_across_stereotype_act.tolist()
    dataframe_counter["Degrees_of_freedom"] = df_counterpart_across_stereotype_act.tolist()
    dataframe_counter["Confidence_interval"] = scipy.stats.t.ppf(q=1 - .05 / 2, df=dataframe_counter["Degrees_of_freedom"]) * \
                                           dataframe_counter["Standard_error"]

    dataframe_complete = pd.concat([dataframe_org, dataframe_counter])
    dataframe_complete = dataframe_complete.rename(columns={vignette_column: "Mean Predicted Grade"})
    dataframe_complete["Stereotype Activation"] = pd.Categorical(dataframe_complete.index, categories=["None", "CaseBased", "Statistics"], ordered=True)
    dataframe_complete.index = dataframe_complete.index + "-" + dataframe_complete["Sex"]
    dataframe_complete = dataframe_complete.reindex(["None-Female", "CaseBased-Female", "Statistics-Female", "None-Male", "CaseBased-Male", "Statistics-Male"])

    return dataframe_complete


def prepare_to_visualize_multiple(data, vignette_of_interest, is_vignette_female, title, fig_name, legend):
    if legend:
        leg_pos = (0.961, .5)
    else:
        leg_pos = 'none'
    pd = p9.position_dodge(width=0.4)
    mean_and_se_data = calculate_means_and_standard_errors(data, vignette_of_interest, is_vignette_female)
    plot = (p9.ggplot(mean_and_se_data) +
            p9.aes("Stereotype Activation", "Mean Predicted Grade", color="Sex") +
            p9.geom_point(position=pd, size=5, show_legend=False) +
            p9.geom_errorbar(p9.aes(ymin=mean_and_se_data["Mean Predicted Grade"] - mean_and_se_data["Confidence_interval"],
                                    ymax=mean_and_se_data["Mean Predicted Grade"] + mean_and_se_data["Confidence_interval"]), width=0.3, alpha=1, position = pd)+
            p9.scale_color_manual({"Female": "indianred", "Male": "royalblue"}) +
            #p9.theme(axis_title_x=p9.element_blank(), axis_text_x=p9.element_blank(), axis_ticks_major=p9.element_blank(), axis_title_y=p9.element_blank(), axis_text_y=p9.element_blank(), legend_position="none")
            p9.labs(x='Stereotype Activation', y="Average Grade Prediction", title=title) +
            p9.scale_y_continuous(breaks=range(6, 17, 2), limits = (6,16)) +
            p9.theme(legend_position=leg_pos, figure_size=(5,5), plot_title=p9.element_text(size=20), text=p9.element_text(size=16), legend_text=p9.element_text(size=18), axis_title_x=p9.element_text(size=18), axis_title_y=p9.element_text(size=18)) # text=p9.element_text(size=24)
            )
    #plot.save(fig_name+".eps", format='eps')
    #print(plot)
    return plot


def visualize_one_plot(data, vignette_of_interest, is_vignette_female, title, fig_name):
    pd = p9.position_dodge(width=0.4)
    mean_and_se_data = calculate_means_and_standard_errors(data, vignette_of_interest, is_vignette_female)
    plot = (p9.ggplot(mean_and_se_data) +
            p9.aes("Stereotype Activation", "Mean Predicted Grade", color="Sex") +
            p9.geom_point(position=pd, size=3, show_legend=False) +
            p9.geom_errorbar(p9.aes(ymin=mean_and_se_data["Mean Predicted Grade"] - mean_and_se_data["Confidence_interval"],
                                    ymax=mean_and_se_data["Mean Predicted Grade"] + mean_and_se_data["Confidence_interval"]), width=0.15, alpha=0.5, position = pd)+
            p9.scale_color_manual({"Female": "indianred", "Male": "royalblue"}) +
            p9.labs(x='Stereotype Activation', y="Average Grade Prediction", title=title) +
            p9.theme(legend_position=(0.961, .5), figure_size=(4, 4))
            )
    plot.save(fig_name+".eps", format='eps')
    #print(plot)
    return plot


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #complete_formatting_and_preprocessing()
    data = load_final_data()
    prof_3 = prepare_to_visualize_multiple(data, 817, is_vignette_female=True, title="Student Profile 3", fig_name = "vignette8", legend=True)
    prof_2 = prepare_to_visualize_multiple(data, 881, is_vignette_female=True, title="Student Profile 2", fig_name = "vignette8", legend=False)
    prof_1 = prepare_to_visualize_multiple(data, 982, is_vignette_female=True, title="Student Profile 1", fig_name = "vignette8", legend=False)


    g1 = pw.load_ggplot(prof_1, figsize=(5, 5))
    g2 = pw.load_ggplot(prof_2, figsize=(5, 5))
    g3 = pw.load_ggplot(prof_3, figsize=(5, 5))

    g123 = (g1 | g2 | g3)

    g123.savefig("results.eps")





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
