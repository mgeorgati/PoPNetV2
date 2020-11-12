library(sf)
library(dplyr)
library(maptools)
library(rgdal)
library(raster)
library(readr)


setwd("C:/FUME/popnetv2/data/pop_tur/selections")
path <-list.files(path = "C:/FUME/popnetv2/data/pop_tur/selections", pattern=".tif", full.names=TRUE)
#Create an empty data frame
df <- data.frame(rasteA=character(), rasterB=character(), correlation=double())
for (i in path) {
  nameI <- path_file(i)
  
  for (j in path) {
    nameJ=path_file(j)
    
    raster1 <- raster(paste(i))
    raster2 <- raster(paste(j))
    stacked <- stack(raster1, raster2)
    names(stacked) <- c(raster1, raster2)
    corr_r <- cor(values(stacked)[,1],values(stacked)[,2],use = "na.or.complete", method="pearson")
    
    if ((corr_r > 0.5)&(corr_r!=1)) {
      de <- list(rasterA=nameI, rasterB=nameJ, correlation=corr_r)
      df = rbind(df,de, stringsAsFactors=FALSE)
    }
  }
}
df[!duplicated(df[ , c("correlation")]),]
