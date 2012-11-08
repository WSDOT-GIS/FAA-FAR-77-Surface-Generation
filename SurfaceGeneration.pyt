"""This script defines an ArcGIS Python Toolbox for generating FAA FAR 77
surfaces.
"""

import os, uuid, re
import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Surface Generation"
        self.alias = "far77"

        # List of tool classes associated with this toolbox
        self.tools = [LineToFar77]

class Far77Params(object):
    """A class used to define FAR 77 surface creation parameters based on 
    runway classification"""
    def __init__(self, runway_type):
        """Creates a Far77Params instance
        @param runway_type: A runway type
        @type runway_type: str
        @rtype: Far77Params
        """
        self.primary_surface_length = 200
        self.primary_surface_width = 0
        self.approach_surface_extendedwidth = 0
        self.first_section_length = 0
        self.first_section_slope = 0
        self.second_section_length = 0
        self.second_section_slope = 0
        self.horizontal_surface_height = 150
        self.horizontal_surface_radius = 0
        self.conical_surface_slope = 20
        self.conical_surface_offset = 4000
        self.transitional_surface_slope = 7
        
        # The runway types listed in the documentation for FAA FAR 77 do not 
        # match what appears when you actually run the tool in ArcMap.
        # These regular expressions should match either version. 
        if re.match("Visual\s*(?:Runway)?\s*Visual\sApproach", runway_type, re.I):
            self.primary_surface_width = 500
            self.approach_surface_extendedwidth = 1500
            self.first_section_length = 5000
            self.first_section_slope = 20
            self.horizontal_surface_radius = 5000
        elif re.match("Utility\s*(?:Runway)?\s*Visual Approach", runway_type, re.I):
            self.primary_surface_width = 250
            self.approach_surface_extendedwidth = 1250
            self.first_section_length = 5000
            self.first_section_slope = 20
            self.horizontal_surface_radius = 5000
        elif re.match("Utility\s*(?:Runway)?\s*Non[\s\-]*Precision Instrument Approach", runway_type, re.I):
             self.primary_surface_width = 500
             self.approach_surface_extendedwidth = 2000
             self.first_section_length = 5000
             self.first_section_slope = 20
             self.horizontal_surface_radius = 5000
        elif re.match("Precision Instrument\s*(?:Runway)?", runway_type, re.I):
             self.primary_surface_width = 1000
             self.approach_surface_extendedwidth = 16000
             self.first_section_length = 10000
             self.first_section_slope = 50
             self.second_section_length = 40000
             self.second_section_slope = 40
             self.horizontal_surface_radius = 10000
        elif re.match("Non Precision Instrument\s*(?:Runway)?\s*(?:(?:High)|(?:Greater)) Visibility", runway_type, re.I):
             self.primary_surface_width = 500
             self.approach_surface_extendedwidth = 3500
             self.first_section_length = 10000
             self.first_section_slope = 34
             self.horizontal_surface_radius = 10000
        elif re.match("Non Precision Instrument\s*(?:Runway)\s*Approach Low Visibility", runway_type, re.I):
             self.primary_surface_width = 1000
             self.approach_surface_extendedwidth = 4000
             self.first_section_length = 10000
             self.first_section_slope = 34
             self.horizontal_surface_radius = 10000

class LineToFar77(object):
    _IN_FEATURES_INDEX = 0
    _PRODUCTION_DB_INDEX = 1
    _ELEVATION_DATA = 2
    _IS_PREPARED_HARD_SURFACE_INDEX = 3
    _RUNWAY_TYPE_INDEX = 4
    _OUTPUT_FEATURE_CLASS_INDEX = 5
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LineToFar77"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        lineFeaturesParam = arcpy.Parameter(
            name="line_features",
            displayName="Line Features",
            direction="Input",
            datatype="Feature Set",
            parameterType="Required")
        # Supply a template for the line feature set.
        lineFeaturesParam.value = os.path.join(os.path.dirname(__file__),
           "Data", "Templates", "ProductionWorkspace.gdb", "Airfield", 
           "RunwayCenterline")
        
        productionLibraryParam = arcpy.Parameter(
             name="production_database",
             displayName="Production Database",
             direction="Input",
             datatype="Workspace")
        
        elevationParam = arcpy.Parameter(
            name="elevation_layer",
            displayName="Elevation Layer",
            direction="Input",
            datatype=["Raster Layer",
                      "LAS Dataset Layer",
                      "Terrain Layer",
                      "TIN Layer"],
            parameterType="Required")

        isPreparedHardSurfaceParam = arcpy.Parameter(
             name="is_prepared_hard_surface",
             displayName="Is prepared hard surface?",
             direction="Input",
             datatype="Boolean",
             parameterType="Optional")
        isPreparedHardSurfaceParam.value = False
        
        
        
        runwayTypeParam = arcpy.Parameter(
              name="runway_type",
              displayName="Runway Type",
              direction="Input",
              datatype="String",
              parameterType="Required"
              )
        runwayTypeParam.filter.type = "ValueList"
        runwayTypeParam.filter.list = [
           "Visual Runway Visual Approach",
           "Utility Runway Visual Approach",
           "Utility Runway Non Precision Instrument Approach",
           "Precision Instrument Runway",
           "Non Precision Instrument Runway High Visibility",
           "Non Precision Instrument Runway Approach Low Visibility"]
        
        outputFCParam = arcpy.Parameter(
            name="output_feature_class",
            displayName="Output Feature Class",
            direction="Output",
            datatype="Feature Class",
            parameterType="Required")
        outputFCParam.value = arcpy.CreateUniqueName("faafar77", arcpy.env.scratchGDB)
        
        params = [lineFeaturesParam, productionLibraryParam, elevationParam, isPreparedHardSurfaceParam, 
                  runwayTypeParam, outputFCParam]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True #arcpy.CheckExtension("3D") and arcpy.CheckExtension("Aeronautical")

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        outputFCParam = parameters[self._OUTPUT_FEATURE_CLASS_INDEX]
        if not outputFCParam.altered:
            outputFCParam.value = arcpy.CreateUniqueName("faafar77", arcpy.env.scratchGDB)
            #outputFCParam.value = os.path.join(arcpy.env.scratchGDB,"far77%s" % uuid.uuid1())
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        productionWSParam = parameters[self._PRODUCTION_DB_INDEX]
        if productionWSParam.altered:
            if not arcpy.Exists(productionWSParam.valueAsText):
                # Add a standard "Workspace does not exist" message.
                productionWSParam.setIDMessage(message_type="ERROR", 
                                               message_ID=000535)
            else:
                # If no problems are detected, clear messages
                productionWSParam.clearMessage()
                pass
        return

    def execute(self, parameters, messages):
        """Creates FAA FAR 77 surfaces
        @param parameters: The parameters for the tool.
        @param messages: The messages for the tool.
        """
        # Feature Set
        in_features = parameters[self._IN_FEATURES_INDEX].value
        in_surface = parameters[self._ELEVATION_DATA].valueAsText
        production_workspace = parameters[self._PRODUCTION_DB_INDEX].valueAsText
        isPreparedHardSurface = parameters[self._IS_PREPARED_HARD_SURFACE_INDEX].value
        runway_type = parameters[self._RUNWAY_TYPE_INDEX].value
        out_featureclass = parameters[self._OUTPUT_FEATURE_CLASS_INDEX].valueAsText
        
        result = arcpy.management.GetCount(in_features)
        inFeatureCount = result.getOutput(0)
        messages.addMessage("in_features: %s" % inFeatureCount)
        inFeatureCount = int(inFeatureCount)
        
        if inFeatureCount <= 0:
            # Use 010151: features found in <value>. Possible empty feature class.  http://resources.arcgis.com/en/help/main/10.1/index.html#//00vq0000000m010151
            # messages.addMessage("in_features contains no features. %s" % inFeatureCount)
            messages.addIDMessage(1, 010151, "in_features")
            return
        
        clear_way_length = 0
        if not isPreparedHardSurface:
            clear_way_length = 200
        
        use_predefined_database_specification = "CUSTOM_SPECIFICATION"
        create_surface = "PRIMARY_SURFACE;APPROACH_SURFACE;HORIZONTAL_SURFACE;CONICAL_SURFACE;TRANSITIONAL_SURFACE"
        
        # Set the other parameters appropriate for the runway type.
        far77Params = Far77Params(runway_type)
        
        primary_surface_length = far77Params.primary_surface_length
        primary_surface_width = far77Params.primary_surface_width
        approach_surface_extendedwidth = far77Params.approach_surface_extendedwidth
        first_section_length = far77Params.first_section_length
        first_section_slope = far77Params.first_section_slope
        second_section_length = far77Params.second_section_length
        second_section_slope = far77Params.second_section_slope
        horizontal_surface_height = far77Params.horizontal_surface_height
        horizontal_surface_radius = far77Params.horizontal_surface_radius
        conical_surface_slope = far77Params.conical_surface_slope
        conical_surface_offset = far77Params.conical_surface_offset
        transitional_surface_slope = far77Params.transitional_surface_slope
        
        messages.addMessage("Executing Interpolate Shape tool")
        # Get the elevations of the runways.  Output will be in a new feature class. 
        # Create the name for the output runways feature class with elevations.
        in_features3D = arcpy.CreateUniqueName("runwayCenterlines", production_workspace)
        
        # Create output feature class.
        out_path, out_name = os.path.split(out_featureclass)
        ##template = os.path.join(os.path.dirname(__file__),
        ##   "Data", "Templates", "ProductionWorkspace.gdb", "Airspace", 
        ##   "ObstructionIdSurface")
        template = os.path.join(production_workspace, "Airspace", 
                                "ObstructionIdSurface")
        messages.addMessage("Creating featureclass %s in %s using template %s..." % (out_name, out_path, template))
        arcpy.management.CreateFeatureclass(out_path, out_name, 
                                            template=template,
                                            has_z="SAME_AS_TEMPLATE")
        
        arcpy.InterpolateShape_3d(in_surface, in_features, in_features3D, 
                                  vertices_only="VERTICES_ONLY")
        
        messages.addMessage("Executing the FAAFAR77 tool")
        
        try:
            # execute the FAA FAR 77 tool
            arcpy.FAAFAR77_aeronautical(in_features3D, 
                                        production_workspace, 
                                        out_featureclass,
                                        clear_way_length, 
                                        runway_type, 
                                        None, # Airport Elevation will come from Z value of in_features3D
                                        "CUSTOM_SPECIFICATION",
                                        "FEET",
                                        "SLOPE",
                                        create_surface,
                                        primary_surface_length,
                                        primary_surface_width, 
                                        approach_surface_extendedwidth,
                                        first_section_length,
                                        first_section_slope,
                                        second_section_length,
                                        second_section_slope,
                                        horizontal_surface_height,
                                        horizontal_surface_radius,
                                        conical_surface_slope,
                                        conical_surface_offset,
                                        transitional_surface_slope)
        except arcpy.ExecuteError as ex:
            messages.AddGPMessages()
            raise
        finally:
            if arcpy.Exists(in_features3D):
                arcpy.management.Delete(in_features3D)
             
        return
