export const NAV_ITEM_IDS = [
  { id: "home", href: "#home", labelKey: "nav.home" },
  { id: "works", href: "#works", labelKey: "nav.works" },
  { id: "about", href: "#about", labelKey: "nav.about" },
  { id: "contact", href: "#contact", labelKey: "nav.contact" },
];

export const SECTION_IDS = NAV_ITEM_IDS.map((item) => item.id);
