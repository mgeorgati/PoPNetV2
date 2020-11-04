library(raster)
library(rgdal)

r <- raster()
raster1 <- list.files(path = "data/List1", pattern = "*.tif$", full.names = T)
raster2 <- list.files(path = "data/List2", pattern = "*.tif$", full.names = T)
l1 <- stack(raster1)
l2 <- stack(raster2)

list1Values <- values(l1)
list2Values <- values(l2)
corValues <- vector(mode = 'numeric')

for (i in 1:dim(list1Values)[1]){
  corValues[i] <- cor(x = list1Values[i,], y = list2Values[i,], method = 'spearman')
}

corRaster <- setValues(r, values = corValues)