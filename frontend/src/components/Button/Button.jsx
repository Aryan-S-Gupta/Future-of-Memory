import "../../styles/Button.css";

/**
 * Button component
 *
 * A reusable styled button component.
 * Props allow customization of:
 * - The displayed label (`title`).
 * - The CSS class for styling (`baseButton`).
 * - The click event handler (`action`).
 *
 * @component
 * @param {Object} props
 * @param {string} props.title - The text to display inside the button.
 * @param {string} props.baseButton - CSS class name(s) applied for styling.
 * @param {function} props.action - Function to execute when the button is clicked.
 *
 * @returns {JSX.Element} A styled button element with a click handler.
 */
function Button({title, baseButton, action}) {
    return (
        <button className={baseButton} onClick={action}>
            {title}
        </button>
    )
}

export default Button;