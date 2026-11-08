# Input

## Overview
Generic shadcn-vue style text input primitive: a styled native `<input>` element with a `v-model` contract implemented via `@vueuse/core`'s `useVModel`. No app-domain logic and no API calls.

## Interface
- `Input` (exported by `index.ts:1`, re-exporting `./Input.vue`)
- Props (`Input.vue:Props`): `defaultValue?: string | number`, `modelValue?: string | number`, `class?: HTMLAttributes['class']`
- Emits (`Input.vue:defineEmits`): `'update:modelValue'` with payload `string | number`
- Two-way binding (`Input.vue:modelValue`): `useVModel(props, 'modelValue', emits, { passive: true, defaultValue: props.defaultValue })`
- Renders `Input.vue:template`: native `<input v-model="modelValue">` styled `flex h-9 w-full rounded-md border border-input ... disabled:cursor-not-allowed disabled:opacity-50`

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Binds to a plain native `<input>`; callers control the `type` via fallthrough attributes (no `type` prop is declared)
- Value type contract is `string | number` only; no built-in validation or sanitization is performed

## Side Effects
- None (input value is local component state surfaced through `update:modelValue`)

## Verification
- Run (from `frontend/`): `npm run build`
