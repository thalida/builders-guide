<template>
<svg class="icon icon__arrow-right" width="22px" height="15px" viewBox="0 0 22 15" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g class="icon__arrow-right__arrow" transform="translate(-121.000000, -800.000000)" fill-rule="nonzero">
        <g transform="translate(0.000000, 775.000000)">
            <g transform="translate(120.000000, 20.000000)">
                <path d="M23,12.493856 C23,12.6264885 22.9474242,12.7537096 22.8535,12.847356 L15.8535,19.847356 C15.6573106,20.0368421 15.3454576,20.0341322 15.1525907,19.8412653 C14.9597238,19.6483984 14.9570139,19.3365455 15.1465,19.140356 L21.293,12.993856 L1.5,12.993856 C1.22385763,12.993856 1,12.7699984 1,12.493856 C1,12.2177136 1.22385763,11.993856 1.5,11.993856 L21.293,11.993856 L15.1465,5.84735601 C14.9570139,5.65116657 14.9597238,5.33931362 15.1525907,5.14644672 C15.3454576,4.95357982 15.6573106,4.95086991 15.8535,5.14035601 L22.8535,12.140356 C22.9474242,12.2340024 23,12.3612235 23,12.493856 Z"></path>
            </g>
        </g>
    </g>
</svg>
</template>

<style lang="scss">
.icon__arrow-right {
    .icon__arrow-right__arrow {
        transition: all 300ms;
    }

    &,
    &.faded {
        .icon__arrow-right__arrow {
            fill: #DBDCDD;
        }
    }

    &.highlighted {
        .icon__arrow-right__arrow {
            fill: #A07532;
        }
    }
}
</style>
