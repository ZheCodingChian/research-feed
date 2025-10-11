import { Checkbox } from './Checkbox';
import { FilterOption } from '../../constants/filterOptions';

interface FilterSectionProps {
  title: string;
  options: FilterOption[];
  selectedValues: string[];
  onSelectionChange: (values: string[]) => void;
}

export function FilterSection({ title, options, selectedValues, onSelectionChange }: FilterSectionProps) {
  const handleCheckboxChange = (optionValue: string, checked: boolean) => {
    if (checked) {
      // Add value to selectedValues
      onSelectionChange([...selectedValues, optionValue]);
    } else {
      // Remove value from selectedValues
      onSelectionChange(selectedValues.filter(v => v !== optionValue));
    }
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Section Title */}
      <h3 className="text-neutral-800 font-header font-bold text-[1rem]">
        {title}
      </h3>

      {/* Checkbox Options */}
      <div className="flex flex-col gap-2">
        {options.map((option) => (
          <Checkbox
            key={option.value}
            id={`${title}-${option.value}`}
            label={option.label}
            checked={selectedValues.includes(option.value)}
            onChange={(checked) => handleCheckboxChange(option.value, checked)}
          />
        ))}
      </div>
    </div>
  );
}
