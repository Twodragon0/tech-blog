import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

interface BlogVideoProps {
	title: string;
	thumbnail: string;
	audioPath: string;
}

export const BlogVideo: React.FC<BlogVideoProps> = ({title, thumbnail, audioPath}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();
	const progress = frame / durationInFrames;

	return (
		<AbsoluteFill
			style={{
				backgroundColor: '#1a1a1a',
				display: 'flex',
				flexDirection: 'column',
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			{/* 배경 이미지 */}
			<AbsoluteFill>
				<Img
					src={staticFile(thumbnail)}
					style={{
						width: '100%',
						height: '100%',
						objectFit: 'cover',
						opacity: 0.3,
					}}
				/>
			</AbsoluteFill>

			{/* 그라데이션 오버레이 */}
			<AbsoluteFill
				style={{
					background: 'linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.5) 50%, rgba(0,0,0,0.7) 100%)',
				}}
			/>

			{/* 제목 */}
			<Sequence from={0} durationInFrames={durationInFrames}>
				<div
					style={{
						position: 'relative',
						zIndex: 1,
						textAlign: 'center',
						padding: '0 80px',
					}}
				>
					<h1
						style={{
							fontSize: 72,
							fontWeight: 'bold',
							color: '#ffffff',
							margin: 0,
							textShadow: '0 4px 20px rgba(0,0,0,0.8)',
							lineHeight: 1.2,
						}}
					>
						{title}
					</h1>
				</div>
			</Sequence>

			{/* 진행 바 */}
			<Sequence from={0} durationInFrames={durationInFrames}>
				<div
					style={{
						position: 'absolute',
						bottom: 40,
						left: 0,
						right: 0,
						height: 4,
						backgroundColor: 'rgba(255,255,255,0.2)',
					}}
				>
					<div
						style={{
							height: '100%',
							width: `${progress * 100}%`,
							backgroundColor: '#ffffff',
						}}
					/>
				</div>
			</Sequence>

			{/* 오디오 */}
			<Audio src={staticFile(audioPath)} />
		</AbsoluteFill>
	);
};
