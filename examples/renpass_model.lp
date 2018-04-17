\* Source Pyomo model name=Model *\

min 
objective:
+0 ONE_VAR_CONSTANT

s.t.

c_e_Bus_balance(bus0_0)_:
+1 flow(reservoir_bus0_0)
= 0.37282961800000003

c_e_Bus_balance(bus0_1)_:
+1 flow(reservoir_bus0_1)
= 0.35482577300000001

c_e_Bus_balance(water_bus_reservoir_0)_:
-1 flow(water_bus_reservoir_reservoir_0)
-1 flow(water_bus_reservoir_water_spillage_reservoir_0)
+1 flow(water_inflow_reservoir_water_bus_reservoir_0)
= 0

c_e_Bus_balance(water_bus_reservoir_1)_:
-1 flow(water_bus_reservoir_reservoir_1)
-1 flow(water_bus_reservoir_water_spillage_reservoir_1)
+1 flow(water_inflow_reservoir_water_bus_reservoir_1)
= 0

c_e_GenericStorageBlock_balance(reservoir_0)_:
+1 GenericStorageBlock_capacity(reservoir_0)
-1 GenericStorageBlock_capacity(reservoir_1)
+1 flow(reservoir_bus0_0)
-1 flow(water_bus_reservoir_reservoir_0)
= 0

c_e_GenericStorageBlock_balance(reservoir_1)_:
-1 GenericStorageBlock_capacity(reservoir_0)
+1 GenericStorageBlock_capacity(reservoir_1)
+1 flow(reservoir_bus0_1)
-1 flow(water_bus_reservoir_reservoir_1)
= 0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= flow(reservoir_bus0_0) <= +inf
   0 <= flow(reservoir_bus0_1) <= +inf
   0 <= flow(water_bus_reservoir_reservoir_0) <= +inf
   0 <= flow(water_bus_reservoir_reservoir_1) <= +inf
   0 <= flow(water_bus_reservoir_water_spillage_reservoir_0) <= +inf
   0 <= flow(water_bus_reservoir_water_spillage_reservoir_1) <= +inf
   0 <= flow(water_inflow_reservoir_water_bus_reservoir_0) <= 1
   0 <= flow(water_inflow_reservoir_water_bus_reservoir_1) <= 1
   0 <= GenericStorageBlock_capacity(reservoir_0) <= 5000
   0 <= GenericStorageBlock_capacity(reservoir_1) <= 5000
end
