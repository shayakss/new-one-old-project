import React, { useState, useEffect, useRef } from 'react';
import { useTheme } from '../contexts/ThemeContext';

const VideoBackground = () => {
  const { theme } = useTheme();
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const videoRef = useRef(null);

  const videoSources = [
    `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/video/5453622-uhd_3840_2160_24fps.mp4`
  ];

  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      const playVideo = async () => {
        try {
          await video.play();
          console.log('Video is playing');
        } catch (error) {
          console.error('Error playing video:', error);
          // If autoplay fails, try to set up a user interaction handler
          if (error.name === 'NotAllowedError') {
            console.log('Autoplay blocked, video will play on user interaction');
          }
        }
      };
      
      if (videoLoaded) {
        playVideo();
      }
    }
  }, [videoLoaded]);

  const handleVideoLoad = () => {
    console.log('Video loaded successfully');
    setVideoLoaded(true);
    setVideoError(false);
  };

  const handleVideoError = (e) => {
    console.error('Video error:', e);
    console.error('Video error details:', e.target.error);
    setVideoError(true);
    setVideoLoaded(false);
  };

  // Add a timeout for video loading
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!videoLoaded && !videoError) {
        console.log('Video loading timeout, showing fallback');
        setVideoError(true);
      }
    }, 10000); // 10 seconds timeout

    return () => clearTimeout(timeout);
  }, [videoLoaded, videoError]);

  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden">
      {/* Video Background */}
      <video
        ref={videoRef}
        className={`absolute top-1/2 left-1/2 min-w-full min-h-full w-auto h-auto transform -translate-x-1/2 -translate-y-1/2 object-cover transition-opacity duration-1000 ${
          videoLoaded ? 'opacity-100' : 'opacity-0'
        }`}
        autoPlay
        muted
        loop
        playsInline
        onLoadedData={handleVideoLoad}
        onError={handleVideoError}
        onLoadStart={() => console.log('Video loading started')}
        onCanPlay={() => console.log('Video can play')}
        onCanPlayThrough={() => console.log('Video can play through')}
        src="/5453622-uhd_3840_2160_24fps.mp4"
        poster="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjMUYyOTM3Ii8+CjxwYXRoIGQ9Ik0wIDBoMTAwdjEwMEgweiIgZmlsbD0iIzFGMjkzNyIvPgo8L3N2Zz4="
      />
      
      {/* Fallback Background - shows when video fails to load */}
      {(videoError || !videoLoaded) && (
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 animate-pulse"></div>
      )}
      
      {/* Video Overlay */}
      <div className="absolute inset-0 bg-black/40 dark:bg-black/60 transition-all duration-300"></div>
      
      {/* Theme-specific overlay */}
      <div className="absolute inset-0 bg-white/20 dark:bg-transparent transition-all duration-300"></div>
      
      {/* Loading indicator */}
      {!videoLoaded && !videoError && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
        </div>
      )}
    </div>
  );
};

export default VideoBackground;