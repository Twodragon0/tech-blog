import {
	AbsoluteFill,
	Audio,
	Img,
	Sequence,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
	interpolate,
	Easing,
} from 'remotion';

interface ScriptSegment {
	text: string;
	startTime: number;
	duration: number;
	image?: string;
}

interface BlogVideoProps {
	title: string;
	thumbnail: string;
	audioPath: string;
	segments?: ScriptSegment[];
}

export const BlogVideo: React.FC<BlogVideoProps> = ({
	title,
	thumbnail,
	audioPath,
	segments = [],
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	return (
		<AbsoluteFill
			style={{
				backgroundColor: '#000000',
			}}
		>
			{/* 세그먼트별 이미지 표시 */}
			{segments.map((segment, index) => {
				const startFrame = segment.startTime * fps;
				const endFrame = (segment.startTime + segment.duration) * fps;
				const segmentFrames = endFrame - startFrame;

				if (frame < startFrame || frame >= endFrame) {
					return null;
				}

				const segmentImage = segment.image || thumbnail;

				return (
					<Sequence
						key={index}
						from={startFrame}
						durationInFrames={segmentFrames}
					>
						<AbsoluteFill>
							<Img
								src={staticFile(segmentImage)}
								style={{
									width: '100%',
									height: '100%',
									objectFit: 'contain',
									opacity: interpolate(
										frame,
										[startFrame, startFrame + 10, endFrame - 10, endFrame],
										[0, 1, 1, 0],
										{
											easing: Easing.ease,
											extrapolateLeft: 'clamp',
											extrapolateRight: 'clamp',
										}
									),
								}}
							/>
						</AbsoluteFill>
					</Sequence>
				);
			})}

			{/* 기본 썸네일 (세그먼트가 없을 때) */}
			{segments.length === 0 && (
				<AbsoluteFill>
					<Img
						src={staticFile(thumbnail)}
						style={{
							width: '100%',
							height: '100%',
							objectFit: 'contain',
						}}
					/>
				</AbsoluteFill>
			)}


			{/* 오디오 */}
			<Audio src={staticFile(audioPath)} />
		</AbsoluteFill>
	);
};
