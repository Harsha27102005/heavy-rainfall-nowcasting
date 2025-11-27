import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

const PageTransition = ({ children }) => {
  const location = useLocation();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [displayLocation, setDisplayLocation] = useState(location);

  useEffect(() => {
    if (location !== displayLocation) {
      setIsTransitioning(true);
      
      // Short delay to show exit animation
      const timer = setTimeout(() => {
        setDisplayLocation(location);
        setIsTransitioning(false);
      }, 150);

      return () => clearTimeout(timer);
    }
  }, [location, displayLocation]);

  return (
    <div
      className={`
        min-h-screen transition-all duration-300 ease-in-out
        ${isTransitioning 
          ? 'opacity-0 transform translate-x-4' 
          : 'opacity-100 transform translate-x-0'
        }
      `}
    >
      {children}
    </div>
  );
};

export default PageTransition;



