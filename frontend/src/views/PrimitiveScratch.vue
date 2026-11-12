<script setup lang="ts">
// TEMPORARY scratch usage for primitive authoring verification (task 1.1/1.3).
// Removed before the phase commit; evidence screenshots live in tests/evidence/g1-primitives/.
import { ref } from 'vue'
import { Toggle } from '@/components/ui/toggle'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { Checkbox } from '@/components/ui/checkbox'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'

const toggleOn = ref(true)
const single = ref('a')
const multi = ref<string[]>(['a', 'c'])
const checked = ref(true)
const unchecked = ref(false)
const switchOn = ref(true)
const switchOff = ref(false)
const price = ref([500])
const range = ref([200, 800])
const sheetOpen = ref(false)
</script>

<template>
  <main class="mx-auto max-w-3xl space-y-8 p-8">
    <h1 class="text-lg font-semibold">Primitive scratch — dev only</h1>

    <section class="space-y-2">
      <h2 class="text-sm font-medium text-muted-foreground">Toggle</h2>
      <div class="flex items-center gap-3">
        <Toggle v-model="toggleOn" variant="outline">Bold</Toggle>
        <Toggle :default-pressed="false">Italic</Toggle>
        <Toggle variant="outline" size="sm" disabled>Disabled</Toggle>
      </div>
    </section>

    <section class="space-y-2">
      <h2 class="text-sm font-medium text-muted-foreground">ToggleGroup — single / multiple</h2>
      <ToggleGroup v-model="single" type="single" variant="outline">
        <ToggleGroupItem value="a">Alpha</ToggleGroupItem>
        <ToggleGroupItem value="b">Beta</ToggleGroupItem>
        <ToggleGroupItem value="c">Gamma</ToggleGroupItem>
      </ToggleGroup>
      <div>single value: {{ single }}</div>
      <ToggleGroup v-model="multi" type="multiple" variant="outline" :spacing="8">
        <ToggleGroupItem value="a">Alpha</ToggleGroupItem>
        <ToggleGroupItem value="b">Beta</ToggleGroupItem>
        <ToggleGroupItem value="c">Gamma</ToggleGroupItem>
      </ToggleGroup>
      <div>multi values: {{ multi.join(', ') }}</div>
    </section>

    <section class="space-y-2">
      <h2 class="text-sm font-medium text-muted-foreground">Checkbox</h2>
      <label class="flex items-center gap-2"><Checkbox v-model="checked" /> checked</label>
      <label class="flex items-center gap-2"><Checkbox v-model="unchecked" /> unchecked</label>
      <label class="flex items-center gap-2"><Checkbox disabled /> disabled</label>
    </section>

    <section class="space-y-2">
      <h2 class="text-sm font-medium text-muted-foreground">Switch</h2>
      <label class="flex items-center gap-2"><Switch v-model="switchOn" /> on</label>
      <label class="flex items-center gap-2"><Switch v-model="switchOff" /> off</label>
      <label class="flex items-center gap-2"><Switch disabled /> disabled</label>
    </section>

    <section class="space-y-4">
      <h2 class="text-sm font-medium text-muted-foreground">Slider</h2>
      <Slider v-model="price" :min="0" :max="1000" :step="50" />
      <div>price: {{ price[0] }}</div>
      <Slider v-model="range" :min="0" :max="1000" :step="50" />
      <div>range: {{ range[0] }} – {{ range[1] }}</div>
    </section>

    <section class="space-y-2">
      <h2 class="text-sm font-medium text-muted-foreground">Sheet (side right)</h2>
      <Sheet v-model:open="sheetOpen">
        <SheetTrigger as-child>
          <button class="rounded-md border px-3 py-1.5 text-sm">Open sheet</button>
        </SheetTrigger>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Filter sheet</SheetTitle>
            <SheetDescription>Scratch verification of the sheet primitive.</SheetDescription>
          </SheetHeader>
          <div class="grid gap-4 p-4">
            <label class="flex items-center gap-2"><Checkbox :default-checked="true" /> Fungal-acne safe</label>
            <label class="flex items-center gap-2"><Switch :default-checked="true" /> Strict exclusions</label>
            <Slider :default-value="[400]" :min="0" :max="1000" :step="50" />
          </div>
          <SheetFooter>
            <SheetClose as-child>
              <button class="rounded-md border px-3 py-1.5 text-sm">Close</button>
            </SheetClose>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </section>
  </main>
</template>
