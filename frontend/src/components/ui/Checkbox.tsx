interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  id: string;
}

export function Checkbox({ checked, onChange, label, id }: CheckboxProps) {
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === ' ' || event.key === 'Enter') {
      event.preventDefault();
      onChange(!checked);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        id={id}
        role="checkbox"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        onKeyDown={handleKeyDown}
        className={`
          w-[1.2rem] h-[1.2rem] flex items-center justify-center
          rounded-[0.2rem]
          outline-none
          ${checked
            ? 'bg-neutral-300'
            : 'bg-neutral-300'
          }
        `}
        tabIndex={0}
      >
        {checked && (
          <svg width="10" height="8" viewBox="0 0 10 8" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9.88913 0.981536L9.0864 0.119118C8.9382 -0.039706 8.69896 -0.039706 8.55113 0.119118L3.73817 5.28999L1.44887 2.81266C1.30104 2.65384 1.0618 2.65384 0.913596 2.81266L0.110873 3.67508C-0.0369576 3.83431 -0.0369576 4.09133 0.110873 4.25016L3.46772 7.88088C3.61555 8.03971 3.85516 8.03971 4.00299 7.88088L9.88913 1.55662C10.037 1.3982 10.037 1.14036 9.88913 0.981536Z" fill="#4F4E4B"/>
          </svg>
        )}
      </button>
      <label
        htmlFor={id}
        className="text-neutral-700 font-header font-normal text-[1rem] cursor-pointer select-none"
        onClick={() => onChange(!checked)}
      >
        {label}
      </label>
    </div>
  );
}
