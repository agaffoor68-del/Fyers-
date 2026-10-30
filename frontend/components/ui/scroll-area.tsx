"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ScrollArea as PrimitiveScrollArea } from "react-custom-scrollbars";

const ScrollArea = React.forwardRef<
  React.ElementRef<typeof PrimitiveScrollArea>,
  React.ComponentPropsWithRef<typeof PrimitiveScrollArea>
>(({ className, children, ...props }, ref) => (
  <PrimitiveScrollArea
    ref={ref}
    className={cn("relative overflow-hidden", className)}
    {...props}
  >
    <div className="relative h-full w-full">{children}</div>
    <PrimitiveScrollArea.Scrollbars>
      <PrimitiveScrollArea.TrackHorizontal />
      <PrimitiveScrollArea.TrackVertical />
    </PrimitiveScrollArea.Scrollbars>
  </PrimitiveScrollArea>
));
ScrollArea.displayName = "ScrollArea";

const ScrollBar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("absolute inset-0", className)} {...props} />
));
ScrollBar.displayName = "ScrollBar";

export { ScrollArea, ScrollBar };
