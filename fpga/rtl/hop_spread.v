// Hop register and DSSS mixer for beamform_top.
// Host writes the next dwell's freq_word at 0x04 and the 31-chip code at 0x80.
module hop_spread (
    input  wire               clk,
    input  wire               chip_tick,
    input  wire signed [15:0] sample_in,
    input  wire [30:0]        chips,
    output reg  signed [15:0] sample_out,
    output reg  [4:0]         chip_idx
);
    always @(posedge clk) begin
        if (chip_tick) chip_idx <= chip_idx + 1;
        if (chips[chip_idx]) sample_out <= sample_in;
        else sample_out <= -sample_in;
    end
endmodule
