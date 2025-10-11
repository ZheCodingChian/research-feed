import { useState, useEffect, useRef, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './HIndexRangeSlider.css';

interface HIndexRangeSliderProps {
  title: string;
  absoluteMax: number;
  urlParamKey: string;
}

export function HIndexRangeSlider({
  title,
  absoluteMax,
  urlParamKey,
}: HIndexRangeSliderProps) {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse and validate initial range from URL
  const getInitialRange = (): [number, number] => {
    const param = searchParams.get(urlParamKey);
    if (!param || param === 'all') return [0, absoluteMax];

    const parts = param.split('-');
    if (parts.length !== 2) return [0, absoluteMax];

    const min = parseInt(parts[0]);
    const max = parseInt(parts[1]);

    // Validate
    if (isNaN(min) || isNaN(max)) return [0, absoluteMax];
    if (min < 0 || max < 0) return [0, absoluteMax];
    if (min > max) return [0, absoluteMax];

    // Clamp to absoluteMax
    const clampedMax = Math.min(max, absoluteMax);
    const clampedMin = Math.min(min, clampedMax);

    return [clampedMin, clampedMax];
  };

  const [localRange, setLocalRange] = useState<[number, number]>(getInitialRange);

  // Track last committed value to detect external URL changes
  const lastCommittedRange = useRef<string>(searchParams.get(urlParamKey) || 'all');

  // Track absoluteMax changes (date filter changes)
  const prevAbsoluteMax = useRef<number | null>(null);

  useEffect(() => {
    // Only reset if absoluteMax actually CHANGED (not initial mount)
    if (prevAbsoluteMax.current !== null && prevAbsoluteMax.current !== absoluteMax) {
      const currentParam = searchParams.get(urlParamKey);

      // ONLY reset if currently showing "all" range
      // If user has custom range, adjust it instead of resetting
      if (!currentParam || currentParam === 'all') {
        setLocalRange([0, absoluteMax]);
        lastCommittedRange.current = 'all';
        const newParams = new URLSearchParams(searchParams);
        newParams.set(urlParamKey, 'all');
        setSearchParams(newParams);
      } else {
        // User has custom range - clamp to new max but preserve their selection
        const clampedMax = Math.min(localRange[1], absoluteMax);
        const clampedMin = Math.min(localRange[0], clampedMax);
        setLocalRange([clampedMin, clampedMax]);
      }
    }
    prevAbsoluteMax.current = absoluteMax;
  }, [absoluteMax, urlParamKey, searchParams, setSearchParams, localRange]);

  // Memoize URL param value to prevent unnecessary re-renders
  const urlParamValue = useMemo(() => searchParams.get(urlParamKey) || 'all', [searchParams, urlParamKey]);

  // Sync from URL only if it changed externally (browser back/forward/bookmark)
  useEffect(() => {
    const currentURLValue = urlParamValue;

    // If URL value different from our last commit → external change
    if (currentURLValue !== lastCommittedRange.current) {
      if (currentURLValue === 'all') {
        setLocalRange([0, absoluteMax]);
      } else {
        const parts = currentURLValue.split('-');
        if (parts.length === 2) {
          const min = parseInt(parts[0]);
          const max = parseInt(parts[1]);
          if (!isNaN(min) && !isNaN(max)) {
            const clampedMax = Math.min(max, absoluteMax);
            const clampedMin = Math.min(min, clampedMax);
            setLocalRange([clampedMin, clampedMax]);
          }
        }
      }
      lastCommittedRange.current = currentURLValue;
    }
  }, [urlParamValue, absoluteMax, urlParamKey]);

  const handleChange = (value: number | number[]) => {
    // Update local state (display text will auto-update)
    setLocalRange(value as [number, number]);
  };

  const handleAfterChange = (value: number | number[]) => {
    const range = value as [number, number];
    const newParams = new URLSearchParams(searchParams);

    let urlValue: string;
    if (range[0] === 0 && range[1] === absoluteMax) {
      urlValue = 'all';
      newParams.set(urlParamKey, 'all');
    } else {
      urlValue = `${range[0]}-${range[1]}`;
      newParams.set(urlParamKey, urlValue);
    }

    // Update reference BEFORE setting params (prevents circular update)
    lastCommittedRange.current = urlValue;
    setSearchParams(newParams);
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Header */}
      <h3 className="text-neutral-800 font-header font-bold text-[1rem]">
        {title}
      </h3>

      {/* Display Text */}
      <div className="text-neutral-700 font-header text-[1rem] font-[700]">
        {localRange[0]} - {localRange[1]}
      </div>

      {/* Slider */}
      <div className="px-1">
        <Slider
          range
          min={0}
          max={absoluteMax}
          step={1}
          value={localRange}
          onChange={handleChange}
          onChangeComplete={handleAfterChange}
          pushable={1}
          allowCross={false}
          styles={{
            track: {
              backgroundColor: '#4f4e4b',
            },
            tracks: {
              backgroundColor: '#4f4e4b',
            },
            rail: {
              backgroundColor: '#86857f',
            },
            handle: {
              backgroundColor: '#6b6a65',
              borderColor: '#4f4e4b',
              opacity: 1,
              boxShadow: 'none',
            },
          }}
          className="rc-slider-neutral"
        />
      </div>
    </div>
  );
}
