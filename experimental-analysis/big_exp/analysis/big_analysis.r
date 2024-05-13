library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)

# Load all the data into R

files_gfp = c('day_1_gfp_clean.csv', 'day_2_gfp_clean.csv', 'day_3_gfp_clean.csv')
files_mch = c('day_1_mch_clean.csv', 'day_2_mch_clean.csv', 'day_3_mch_clean.csv')

gfp_times <- c(60*60*2.25,60*60*2.75)
mch_times <- c(60*60*2.50,60*60*3)


filenames <- c(files_gfp, files_mch)

experiment_ID <- 0

# Combine data into a complete dataframe with normalized valuies   ----------------------
master_df = data.frame()
for (filename in files_gfp){
  csv_data <- read.csv(filename) # Load in the data
  experiment_ID <- experiment_ID + 1
  
  # Merge technical replicates
  csv_data <- csv_data %>% group_by(strain, rbs, time)
  csv_data <- csv_data %>% dplyr::summarize(GFP_high = mean(GFP_high), GFP_low = mean(GFP_low), OD600 = mean(OD600))
  
  
  # Create a normalized fluorescence value
  tmp_df <- csv_data %>% filter(is.finite(OD600)) %>% filter(is.finite(GFP_high)) %>% filter(is.finite(GFP_low))
  conversion = lm(formula = GFP_high ~ GFP_low, data = tmp_df)
  linearconversion <- function(v_low, v_high){
    y <- as.numeric()
    if (is.finite(v_high)){
      y <- v_high
    }
    else{
      y <- as.numeric(coef(conversion)[1]) + as.numeric(coef(conversion)[2])*v_low
    }
    y
  }
  csv_data$fluor_norm <- mapply(csv_data$GFP_low, csv_data$GFP_high, FUN=linearconversion)
  csv_data$fluor_norm <- csv_data$fluor_norm/csv_data$OD600
  csv_data$lnOD600 <- log(csv_data$OD600)
  csv_data$experiment <- experiment_ID
  csv_data$groupID <- paste(csv_data$experiment, 
                            csv_data$strain,
                            csv_data$rbs)
  
  # Fix time
  csv_data$time <- round(csv_data$time/900)*900
  
  # Create sliding windows
  processed_data <- data.frame()
  for (sample in unique(csv_data$groupID)){
    subset <- csv_data %>% filter(groupID == sample)
    subset$expression <- c(NaN, 3600*diff(subset$fluor_norm)/900)
    subset$growthrate <- c(NaN, 3600*diff(subset$lnOD600)/900)
    processed_data <- rbind(processed_data, subset)
  }
  
  # Add it to the master dataframe
  master_df = rbind(master_df, processed_data)
}



for (filename in files_mch){
  csv_data <- read.csv(filename) # Load in the data
  experiment_ID <- experiment_ID + 1
  
  # Merge technical replicates
  csv_data <- csv_data %>% group_by(strain, rbs, time)
  csv_data <- csv_data %>% dplyr::summarize(mCherry_high = mean(mCherry_high), mCherry_low = mean(mCherry_low), OD600 = mean(OD600))
  
  
  # Create a normalized fluorescence value
  tmp_df <- csv_data %>% filter(is.finite(OD600)) %>% filter(is.finite(mCherry_high)) %>% filter(is.finite(mCherry_low))
  conversion = lm(formula = mCherry_high ~ mCherry_low, data = tmp_df)
  linearconversion <- function(v_low, v_high){
    y <- as.numeric()
    if (is.finite(v_high)){
      y <- v_high
    }
    else{
      y <- as.numeric(coef(conversion)[1]) + as.numeric(coef(conversion)[2])*v_low
    }
    y
  }
  csv_data$fluor_norm <- mapply(csv_data$mCherry_low, csv_data$mCherry_high, FUN=linearconversion)
  csv_data$fluor_norm <- csv_data$fluor_norm/csv_data$OD600
  csv_data$experiment <- experiment_ID
  csv_data$lnOD600 <- log(csv_data$OD600)
  csv_data$groupID <- paste(csv_data$experiment, 
                            csv_data$strain,
                            csv_data$rbs)
  
  # Fix time
  csv_data$time <- round(csv_data$time/900)*900  
  
  # Create sliding windows
  processed_data <- data.frame()
  for (sample in unique(csv_data$groupID)){
    subset <- csv_data %>% filter(groupID == sample)
    subset$expression <- c(NaN, diff(subset$fluor_norm)/900)
    subset$growthrate <- c(NaN, 3600*diff(subset$lnOD600)/900)
    processed_data <- rbind(processed_data, subset)
  }
  
  # Add it to the master dataframe
  master_df = rbind(master_df, processed_data)
}
write.csv(master_df, file = "tidy_combined.csv")



# Make a dataset that merges the biological replicates (for graphing purposes)   ------------------

mean_df <- master_df %>% group_by(strain, rbs, time)
mean_df <- mean_df %>% dplyr::summarize(GFP_high = mean(GFP_high),
                                        GFP_low = mean(GFP_low),
                                        mCherry_high = mean(mCherry_high),
                                        mCherry_low = mean(mCherry_low),
                                        fluor_norm = mean(fluor_norm),
                                        OD600 = mean(OD600),
                                        expression = mean(expression),
                                        growthrate = mean(growthrate))



# Graphs of each CDS   --------------------------

plot_theme <- theme(plot.title = element_text(family = "Fira Sans Condensed", colour="white"),
                    plot.background = element_rect(fill = "#31363B"),
                    panel.background = element_blank(),
                    panel.grid.major = element_line(color = "grey70", size = 0.2),
                    panel.grid.minor = element_line(color = "grey70", size = 0.2),
                    legend.background = element_blank(),
                    axis.ticks = element_blank(),
                    legend.key = element_blank(),
                    legend.text = element_text(colour = "white"),
                    legend.title = element_text(colour = "white"),
                    axis.text.x=element_text(colour="white"),
                    axis.text.y=element_text(colour="white"),
                    axis.title.x=element_text(colour="white"),
                    axis.title.y=element_text(colour="white"),
                    )

graph_strain<- function(strain_dataframe_master, strain_dataframe_mean, strain_name){
  
  if (strain_name %like% "GFP"){
    t1 <- gfp_times[1]
    t3 <- gfp_times[2]
  } else if (strain_name %like% "MCH"){
    t1 <- mch_times[1]
    t3 <- mch_times[2]
  } else{
    t1 <- 0
    t3 <- 0
  }
  
  p1 <- ggplot() + 
    geom_line(data=strain_dataframe_master, aes(x = time, y = OD600, color=rbs, group=groupID, alpha = 0.05)) +
    geom_line(data=strain_dataframe_mean, aes(x = time, y = OD600, color=rbs), size = 2) +
    ggtitle(paste("Growth of", strain_name, "strain under IPTG Induction")) + 
    plot_theme + ylab("OD600") +scale_x_time() +
    geom_vline(xintercept=t1, linetype='dashed') +
    geom_vline(xintercept=t3, linetype='dashed')
  
  p2 <- ggplot() + 
    geom_line(data=strain_dataframe_master, aes(x = time, y = fluor_norm, color=rbs, group=groupID, alpha = 0.05)) +
    geom_line(data=strain_dataframe_mean, aes(x = time, y = fluor_norm, color=rbs), size = 2) +
    ggtitle(paste("Fluorescence of ", strain_name, "strain under IPTG Induction")) + 
    plot_theme + ylab("AU") +scale_x_time() +
    geom_vline(xintercept=t1, linetype='dashed') +
    geom_vline(xintercept=t3, linetype='dashed')
  
  p3 <- ggplot()+
    geom_line(data=strain_dataframe_master, aes(x = time, y = growthrate, color=rbs, group=groupID, alpha = 0.05)) +
    geom_line(data=strain_dataframe_mean, aes(x = time, y = growthrate, color=rbs), size = 2) +
    ggtitle(paste("Growth Rate of ", strain_name, "strain under IPTG Induction")) + 
    plot_theme + ylab("Growth Rate") +scale_x_time() +
    geom_vline(xintercept=t1, linetype='dashed') +
    geom_vline(xintercept=t3, linetype='dashed')
  
  p4 <- ggplot()+
    geom_line(data=strain_dataframe_master, aes(x = time, y = expression, color=rbs, group=groupID, alpha = 0.05)) +
    geom_line(data=strain_dataframe_mean, aes(x = time, y = expression, color=rbs), size = 2) +
    ggtitle(paste("Expression of ", strain_name, "strain under IPTG Induction")) + 
    plot_theme + ylab("AU/second") +scale_x_time() +
    geom_vline(xintercept=t1, linetype='dashed') +
    geom_vline(xintercept=t3, linetype='dashed')
   
  
  show(p1 + p2 + p3 + p4)

}

for (cds in unique(master_df$strain)){
  graph_master <- master_df %>% filter(strain==cds)
  graph_mean <- mean_df %>% filter(strain==cds)
  graph_strain(graph_master,
               graph_mean,
               cds)
  Sys.sleep(2)
}

# Find the peak expression values for each sample

peaks <- data.frame()

for (sample in unique(master_df$groupID)){
    graph_master <- master_df %>% filter(groupID == sample)
    expression_peak <- graph_master[which.max(graph_master$expression),]
    peaks <- rbind(peaks, expression_peak)
}


gfp_peaks <- peaks %>% filter(strain %like% "GFP")
mch_peaks <- peaks %>% filter(strain %like% "GFP")


p5 <- ggplot() +
  geom_point(data= gfp_peaks,
             aes(x = expression, y = growthrate, color=strain, group=groupID), size=5) +
  ggtitle(paste("Burden of GFP expression")) + 
  plot_theme + ylab("Growth Rate") + xlab("Expression")
#p5


p6 <- ggplot() +
  geom_point(data= mch_peaks,
             aes(x = expression, y = growthrate, color=strain, group=groupID), size=5) +
  ggtitle(paste("Burden of mCherry expression")) + 
  plot_theme + ylab("Growth Rate") + xlab("Expression")
#p6


df_exponential_averages <- data.frame(matrix(ncol = 5, nrow = 0))
colnames(df_exponential_averages) <- c("ID", "strain", "rbs", "growth_rate_od", "output")

IDs <- unique(master_df$groupID)

for (ID_tgt in IDs){
  
  if (ID_tgt %like% "GFP"){
    t1 <- gfp_times[1]
    t3 <- gfp_times[2]
  } else if (ID_tgt %like% "MCH"){
    t1 <- mch_times[1]
    t3 <- mch_times[2]
  } else{
    t1 <- 0
    t3 <- 0
  }
  
  t1_data <- filter(master_df, time == t1, groupID == ID_tgt)
  t3_data <- filter(master_df, time == t3, groupID == ID_tgt)
  growth_rate_od600 = 3600*(log(t3_data[1, "OD600"]) - log(t1_data[1, "OD600"]))/(t3_data[1, "time"] - t1_data[1, "time"])
  output_data = 3600*(t3_data[1, "fluor_norm"] - t1_data[1, "fluor_norm"])/(t3_data[1, "time"] - t1_data[1, "time"])
  df_exponential_averages[nrow(df_exponential_averages) + 1,] = c(ID_tgt, 
                                                                  t1_data$strain[1], 
                                                                  t1_data$rbs[1], 
                                                                  growth_rate_od600,
                                                                  output_data)
  
}

gfp_df_exponential_averages <- df_exponential_averages %>% filter(strain %like% "GFP")
mch_df_exponential_averages <- df_exponential_averages %>% filter(strain %like% "MCH")

p7 <- ggplot() +
  geom_point(data= gfp_df_exponential_averages,
             aes(x = output, y = growth_rate_od, color=strain, group=ID), size=5) +
  ggtitle(paste("Burden of GFP expression")) + 
  plot_theme + ylab("Growth Rate") + xlab("Expression")
p7


p8 <- ggplot() +
  geom_point(data= mch_df_exponential_averages,
             aes(x = output, y = growth_rate_od, color=strain, group=ID), size=5) +
  ggtitle(paste("Burden of mCherry expression")) + 
  plot_theme + ylab("Growth Rate") + xlab("Expression")
p8

