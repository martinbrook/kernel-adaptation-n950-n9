#!/bin/sh

DEBUG_SUFFIX=n950-debug
SUFFIX=n950
HW=n950
EXTRA=20130129.1

sed -e "s/SUFFIX/${SUFFIX}/" \
    -e "s/HARDWARE/${HW}/" \
    -e "s/KERNEL_EXTRA_VERSION/${EXTRA}/" \
    -e "s/CONFLICT/${DEBUG_SUFFIX}/" \
    kernel-adaptation-n950.spec.tpl > kernel-adaptation-n950.spec

sed -e "s/SUFFIX/${DEBUG_SUFFIX}/" \
    -e "s/HARDWARE/${HW}/" \
    -e "s/KERNEL_EXTRA_VERSION/${EXTRA}/" \
    -e "s/CONFLICT/${SUFFIX}/" \
    kernel-adaptation-n950.spec.tpl > kernel-adaptation-n950-debug.spec
 
