// frontend/src/components/MapLegend.js
import React from 'react';

const MapLegend = () => {
    return (
        <div className="mt-6 p-4 bg-white rounded-md shadow-md text-sm">
            <h3 className="text-lg font-medium mb-2">Map Legend</h3>
            <div className="flex items-center mb-2">
                <span className="block w-6 h-6 rounded-full bg-red-500 mr-2"></span>
                <span>Heavy Rainfall Warning Area</span>
            </div>
            <div className="flex items-center mb-2">
                <span className="block w-6 h-6 rounded-full bg-darkblue mr-2"></span>
                <span>Predicted Rain Rate greater than 50mm/h</span>
            </div>
            <div className="flex items-center mb-2">
                <span className="block w-6 h-6 rounded-full bg-blue-500 mr-2"></span>
                <span>Predicted Rain Rate greater than 20mm/h</span>
            </div>
            <div className="flex items-center">
                <span className="block w-6 h-6 rounded-full bg-lightblue mr-2"></span>
                <span>Predicted Rain Rate (General)</span>
            </div>
        </div>
    );
};
export default MapLegend;