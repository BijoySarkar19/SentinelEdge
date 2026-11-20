"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const GRID_SIZE = 18;
type Point = [number, number];

export default function NotFound() {
  const [snake, setSnake] = useState<Point[]>([[8, 8], [8, 9]]);
  const [food, setFood] = useState<Point>([4, 4]);
  const [dir, setDir] = useState<Point>([0, -1]);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const resetGame = () => {
    setSnake([[8, 8], [8, 9]]);
    setFood([4, 4]);
    setDir([0, -1]);
    setScore(0);
    setGameOver(false);
    setIsPlaying(true);
  };

  const moveSnake = useCallback(() => {
    if (gameOver || !isPlaying) return;

    setSnake((prev) => {
      const head = prev[0];
      const newHead: Point = [
        (head[0] + dir[0] + GRID_SIZE) % GRID_SIZE,
        (head[1] + dir[1] + GRID_SIZE) % GRID_SIZE,
      ];

      // Self collision
      if (prev.some(([x, y]) => x === newHead[0] && y === newHead[1])) {
        setGameOver(true);
        return prev;
      }

      const nextSnake = [newHead, ...prev];
      if (newHead[0] === food[0] && newHead[1] === food[1]) {
        setScore((s) => s + 10);
        setFood([
          Math.floor(Math.random() * GRID_SIZE),
          Math.floor(Math.random() * GRID_SIZE),
        ]);
      } else {
        nextSnake.pop();
      }
      return nextSnake;
    });
  }, [dir, food, gameOver, isPlaying]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowUp" && dir[1] !== 1) setDir([0, -1]);
      if (e.key === "ArrowDown" && dir[1] !== -1) setDir([0, 1]);
      if (e.key === "ArrowLeft" && dir[0] !== 1) setDir([-1, 0]);
      if (e.key === "ArrowRight" && dir[0] !== -1) setDir([1, 0]);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [dir]);

  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(moveSnake, 130);
    return () => clearInterval(interval);
  }, [moveSnake, isPlaying]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-4 py-1.5 text-xs font-semibold tracking-wider text-brand-cyan uppercase">
        <span className="h-2 w-2 rounded-full bg-brand-cyan animate-pulse" />
        Signal Lost • Error 404
      </div>
      <h1 className="text-4xl font-extrabold text-text-primary md:text-5xl">Feed Not Found</h1>
      <p className="mt-2 max-w-md text-sm text-text-secondary">
        The requested camera sector or incident report does not exist. Play the Sentinel Drone Patrol mini-game while reconnecting.
      </p>

      {/* Snake Game Terminal */}
      <div className="glass-card mt-6 p-4">
        <div className="mb-3 flex items-center justify-between text-xs text-text-secondary">
          <span>Score: <strong className="text-brand-cyan">{score}</strong></span>
          <span>Use Arrow Keys</span>
        </div>
        <div
          className="relative grid bg-background-secondary rounded-lg border border-white/5"
          style={{
            gridTemplateColumns: `repeat(${GRID_SIZE}, 18px)`,
            gridTemplateRows: `repeat(${GRID_SIZE}, 18px)`,
          }}
        >
          {Array.from({ length: GRID_SIZE * GRID_SIZE }).map((_, i) => {
            const x = i % GRID_SIZE;
            const y = Math.floor(i / GRID_SIZE);
            const isSnake = snake.some(([sx, sy]) => sx === x && sy === y);
            const isHead = snake[0][0] === x && snake[0][1] === y;
            const isFood = food[0] === x && food[1] === y;

            return (
              <div
                key={i}
                className={`h-[18px] w-[18px] rounded-xs transition-colors ${
                  isHead
                    ? "bg-brand-cyan glow-cyan"
                    : isSnake
                    ? "bg-brand-blue/70"
                    : isFood
                    ? "bg-sentinel-critical animate-ping"
                    : ""
                }`}
              />
            );
          })}
        </div>
        <div className="mt-4 flex justify-center gap-3">
          {!isPlaying ? (
            <button
              onClick={resetGame}
              className="rounded-lg bg-brand-cyan px-4 py-2 text-xs font-semibold text-background hover:bg-brand-cyan/80 glow-cyan"
            >
              Start Patrol Game
            </button>
          ) : gameOver ? (
            <button
              onClick={resetGame}
              className="rounded-lg bg-sentinel-critical px-4 py-2 text-xs font-semibold text-white"
            >
              Crashed! Play Again
            </button>
          ) : null}
        </div>
      </div>

      <Link
        href="/dashboard"
        className="mt-8 text-sm font-medium text-brand-cyan hover:underline"
      >
        ← Return to Incident Dashboard
      </Link>
    </div>
  );
}
