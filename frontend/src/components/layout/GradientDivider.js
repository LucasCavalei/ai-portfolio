import React from "react";

const SIZE_CLASS = {
  sm: "gradient-divider--sm",
  md: "gradient-divider--md",
  lg: "gradient-divider--lg",
};

export const GradientDivider = ({
  size = "md",
  animated = true,
  className = "",
}) => (
  <span
    className={[
      "gradient-divider",
      SIZE_CLASS[size] || SIZE_CLASS.md,
      animated && "gradient-divider--animated",
      className,
    ]
      .filter(Boolean)
      .join(" ")}
    aria-hidden="true"
  />
);
