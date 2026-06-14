import React, { useEffect, useRef, useState } from "react";
import { useMediaQuery } from "@material-ui/core";
import { ExpandMore } from "@material-ui/icons";

export const ProjectDescription = ({ description }) => {
  const isMobile = useMediaQuery("(max-width: 768px)");
  const [expanded, setExpanded] = useState(false);
  const [isOverflowing, setIsOverflowing] = useState(false);
  const descriptionRef = useRef(null);

  useEffect(() => {
    if (!isMobile) {
      setExpanded(false);
      setIsOverflowing(false);
      return;
    }

    const el = descriptionRef.current;
    if (!el) return;

    const checkOverflow = () => {
      const lineHeight = parseFloat(window.getComputedStyle(el).lineHeight) || 24;
      const maxCollapsedHeight = lineHeight * 3;
      setIsOverflowing(el.scrollHeight > maxCollapsedHeight + 1);
    };

    checkOverflow();
    window.addEventListener("resize", checkOverflow);
    return () => window.removeEventListener("resize", checkOverflow);
  }, [description, isMobile]);

  const isCollapsed = isMobile && !expanded && isOverflowing;

  return (
    <div
      className={`description-wrapper${
        isCollapsed ? " description-wrapper--collapsed" : ""
      }${expanded ? " description-wrapper--expanded" : ""}`}
    >
      <p ref={descriptionRef} className="description">
        {description}
      </p>
      {isMobile && isOverflowing && (
        <button
          type="button"
          className="description-toggle"
          onClick={() => setExpanded((prev) => !prev)}
          aria-expanded={expanded}
          aria-label={expanded ? "Recolher descrição" : "Ver descrição completa"}
        >
          <ExpandMore
            className={`description-toggle__icon${
              expanded ? " description-toggle__icon--expanded" : ""
            }`}
          />
        </button>
      )}
    </div>
  );
};
