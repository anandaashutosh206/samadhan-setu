import type { Variants, Transition } from "framer-motion";

export const springSnappy: Transition = { type: "spring", stiffness: 400, damping: 28 };
export const springSoft: Transition = { type: "spring", stiffness: 260, damping: 24, mass: 0.9 };

export const pageTransition: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: springSoft },
  exit: { opacity: 0, y: -8 },
};

export const listContainer: Variants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.06, delayChildren: 0.08 } },
};

export const listItem: Variants = {
  initial: { opacity: 0, y: 16, scale: 0.98 },
  animate: { opacity: 1, y: 0, scale: 1, transition: springSoft },
};

export const hoverLift = {
  whileHover: { y: -4, scale: 1.02, transition: springSnappy },
  whileTap: { scale: 0.985 },
};

export const scrollReveal = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0, transition: springSoft },
  viewport: { once: true, margin: "-80px" },
};
